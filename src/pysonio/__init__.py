import re
import urllib.parse
from collections.abc import Generator
from datetime import datetime
from datetime import timedelta
from http import HTTPStatus
from json import JSONDecodeError
from typing import Final
from typing import Optional
from typing import final

import requests
from pydantic import BaseModel
from pydantic import TypeAdapter
from pydantic import ValidationError
from requests import RequestException

from pysonio.content_type import ContentType
from pysonio.endpoints import Endpoint
from pysonio.errors import AuthenticationError
from pysonio.errors import BadRequestError
from pysonio.errors import CommunicationError
from pysonio.errors import ForbiddenError
from pysonio.errors import UnexpectedResponse
from pysonio.models.absence_types import AbsenceTypesData
from pysonio.models.absence_types import ListAbsenceTypesRequest as ListAbsenceTypesRequest
from pysonio.models.absence_types import ListAbsenceTypesResponse as ListAbsenceTypesResponse
from pysonio.models.authentication import AuthErrorResponse
from pysonio.models.authentication import AuthRequest
from pysonio.models.authentication import AuthResponse
from pysonio.models.authentication import AuthToken
from pysonio.models.error_response import ErrorResponse
from pysonio.models.pagination import PaginatedResponse
from pysonio.models.pagination import PaginationQueryParams


@final
class Client:
    _DEFAULT_BASE_URL = "https://api.personio.de"
    _UPPER_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")
    _TOKEN_EXPIRATION_MARGIN_SECONDS = 3 * 60  # 3 minutes

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        personio_partner_identifier: str,
        personio_app_identifier: str,
        scopes: Optional[list[str]] = None,
        base_url: str = _DEFAULT_BASE_URL,
    ) -> None:
        self._client_id: Final = client_id
        self._client_secret: Final = client_secret

        # According to https://developer.personio.de/reference/include-our-headers-in-your-requests,
        # the identifiers must be in upper snake case format.
        if not self._is_upper_snake_case(personio_partner_identifier):
            msg: Final = (
                f"Invalid Personio partner identifier: {personio_partner_identifier}. "
                + "It must be in upper snake case format."
            )
            raise ValueError(msg)
        if not self._is_upper_snake_case(personio_app_identifier):
            msg: Final = (
                f"Invalid Personio app identifier: {personio_app_identifier}. "
                + "It must be in upper snake case format."
            )
            raise ValueError(msg)

        self._personio_headers: Final = {
            "X-Personio-Partner-ID": personio_partner_identifier,
            "X-Personio-App-ID": personio_app_identifier,
        }

        self._scopes: Final = None if scopes is None else " ".join(scopes)

        # The auth token is obtained lazily when needed.
        self._auth_token: Optional[AuthToken] = None

        self._base_url: Final = base_url

    def get_absence_types(self) -> list[AbsenceTypesData]:
        """
        Retrieves a list of all absence types from the Personio API.
        :return: A list of `AbsenceTypesData` instances representing the absence types.
        :raises BadRequestError: If the request fails with a 400 Bad Request status code.
        :raises ForbiddenError: If the request fails with a 403 Forbidden status code.
        :raises UnexpectedResponse: If the response does not match the expected data.
        :raises CommunicationError: If there is a communication error while making the request.
        :raises AuthenticationError: If the authentication process fails.
        """
        # See: https://developer.personio.de/reference/get_v2-absence-types
        responses_generator: Final = self._get_paginated_response(
            endpoint=Endpoint.ABSENCE_TYPES,
            response_model=ListAbsenceTypesResponse,
            expected_status_code=HTTPStatus.OK,
            is_beta_endpoint=True,
        )
        # Flatten the lists and return the result.
        return [absence_type for response in responses_generator for absence_type in response.data]

    def get_absence_type(self, id_: str) -> AbsenceTypesData:
        """
        Retrieves a specific absence type by its ID from the Personio API.
        :param id_: The ID of the absence type to retrieve.
        :return: An `AbsenceTypesData` instance representing the absence type.
        :raises BadRequestError: If the request fails with a 400 Bad Request status code.
        :raises ForbiddenError: If the request fails with a 403 Forbidden status code.
        :raises UnexpectedResponse: If the response does not match the expected data.
        :raises CommunicationError: If there is a communication error while making the request.
        :raises AuthenticationError: If the authentication process fails.
        """
        # See: https://developer.personio.de/reference/get_v2-absence-types-id
        return self._send_get_request(
            endpoint=Endpoint.ABSENCE_TYPES,
            path_params=[id_],
            response_model=AbsenceTypesData,
            is_beta_endpoint=True,
        )

    def _get_paginated_response[ResponseModel: BaseModel](
        self,
        *,
        endpoint: Endpoint,
        response_model: type[ResponseModel],
        expected_status_code: HTTPStatus,
        is_beta_endpoint: bool,
    ) -> Generator[ResponseModel]:
        next_query_params = PaginationQueryParams()
        while True:
            try:
                response = self._send_get_request(
                    endpoint,
                    query_params=next_query_params,
                    response_model=response_model,
                    expected_status_code=expected_status_code,
                    is_beta_endpoint=is_beta_endpoint,
                )
            except UnexpectedResponse as e:
                # We ignore the type error here. This seems to be a false positive from Pyrefly.
                # TODO: Reproduce this error in a minimal example and report it to the Pyrefly team.
                actual_status_code: int = e.response.status_code  # type: ignore[bad-assignment]
                error_response = Client._validate_response(
                    e.response,
                    ErrorResponse,
                    expected_status_code=HTTPStatus(actual_status_code),
                )
                if e.response.status_code == HTTPStatus.BAD_REQUEST:
                    raise BadRequestError(
                        error_response,
                        "Personio API returned a bad request error.",
                    ) from e
                if e.response.status_code == HTTPStatus.FORBIDDEN:
                    raise ForbiddenError(
                        error_response,
                        "Personio API returned a forbidden error.",
                    ) from e
                # We are not able to handle other error codes, so we just re-raise the exception.
                raise

            yield response

            try:
                paginated_response = PaginatedResponse.model_validate(response.model_dump())
            except ValidationError:
                # Pagination has ended.
                break

            next_url_query_params = Client._extract_query_params(paginated_response.meta.links.next.href)
            try:
                next_query_params = PaginationQueryParams.model_validate(next_url_query_params)
            except ValidationError:
                # The `next` link does not contain valid query parameters for the `ListAbsenceTypesRequest` model.
                # We can stop here.
                break

    def _send_get_request[QueryParams: BaseModel, ResponseModel: BaseModel](
        self,
        endpoint: Endpoint,
        *,
        path_params: Optional[list[str]] = None,
        query_params: Optional[QueryParams] = None,
        response_model: type[ResponseModel],
        expected_status_code: HTTPStatus = HTTPStatus.OK,
        is_beta_endpoint: bool = False,
        omit_authentication: bool = False,
    ) -> ResponseModel:
        # We don't want to send empty (`None`) query parameters to the API, so we filter them out.
        query_params_dict: Final = (
            {}
            if query_params is None
            else {key: value for key, value in query_params.model_dump().items() if value is not None}
        )

        url_encoded_params: Final = "" if not query_params_dict else f"?{urllib.parse.urlencode(query_params_dict)}"
        joined_path_params: Final = "" if path_params is None or not path_params else f"/{'/'.join(path_params)}"
        endpoint_url: Final = f"{self._get_endpoint_url(endpoint)}{joined_path_params}"
        url: Final = f"{endpoint_url}{url_encoded_params}"
        headers: Final = self._get_headers(
            content_type=None,
            is_beta_endpoint=is_beta_endpoint,
            omit_authentication=omit_authentication,
        )
        try:
            response: Final = requests.get(
                url,
                headers=headers,
            )
        except RequestException as e:
            msg: Final = f"Failed to send GET request to {url}: {e}"
            raise CommunicationError(msg) from e

        return Client._validate_response(
            response,
            response_model,
            expected_status_code=expected_status_code,
        )

    @staticmethod
    def _extract_query_params(url: str) -> dict[str, str | list[str]]:
        params: Final = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query, keep_blank_values=True)
        # If a query parameter has multiple values, it will be returned as a list.
        return {k: v[0] if len(v) == 1 else v for k, v in params.items()}

    def _send_post_request[Payload: BaseModel, ResponseModel: BaseModel](
        self,
        endpoint: Endpoint,
        *,
        payload: Payload,
        content_type: ContentType,
        response_model: type[ResponseModel],
        expected_status_code: HTTPStatus = HTTPStatus.OK,
        is_beta_endpoint: bool = False,
        omit_authentication: bool = False,
    ) -> ResponseModel:
        url: Final = self._get_endpoint_url(endpoint)
        headers: Final = self._get_headers(
            content_type,
            is_beta_endpoint=is_beta_endpoint,
            omit_authentication=omit_authentication,
        )
        try:
            match content_type:
                case ContentType.X_WWW_FORM_URL_ENCODED:
                    response: Final = requests.post(
                        url,
                        headers=headers,
                        data=payload.model_dump(),
                    )
                case ContentType.JSON:
                    response: Final = requests.post(
                        url,
                        headers=headers,
                        json=payload.model_dump(),
                    )
        except RequestException as e:
            msg: Final = f"Failed to send POST request to {url}: {e}"
            raise CommunicationError(msg) from e

        return Client._validate_response(
            response,
            response_model,
            expected_status_code=expected_status_code,
        )

    def _get_headers(
        self,
        content_type: Optional[ContentType],
        *,
        is_beta_endpoint: bool,
        omit_authentication: bool,
    ) -> dict[str, str]:
        """
        Returns the headers to be used for requests to the Personio API.
        :param is_beta_endpoint: Whether the request is for a beta endpoint.
        :param omit_authentication: Whether to skip authentication for the request.
        :return: A dictionary containing the headers.
        """
        headers: Final = self._personio_headers
        if is_beta_endpoint:
            headers["Beta"] = "true"
        headers["Accept"] = "application/json"
        if content_type is not None:
            headers["Content-Type"] = content_type.value
        if not omit_authentication:
            auth_token: Final = self._get_auth_token()
            headers["Authorization"] = f"Bearer {auth_token.access_token}"
        return headers

    @staticmethod
    def _validate_response[ResponseModel: BaseModel](
        response: requests.Response,
        response_model: type[ResponseModel],
        *,
        expected_status_code: HTTPStatus,
    ) -> ResponseModel:
        """
        Validates the response from the Personio API against the expected response model.
        :param response: The response object from the requests library.
        :param response_model: The expected response model to validate against.
        :param expected_status_code: The expected status code of the response.
        :return: The validated response model instance.
        :raises UnexpectedResponse: If the response does not match the expected model.
        """
        if response.status_code != expected_status_code:
            msg: Final = f"Unexpected status code {response.status_code}. Expected {expected_status_code}."
            raise UnexpectedResponse(response, msg)

        try:
            # We use `TypeAdapter` to validate the response against the expected model because it has a generic
            # return type. Calling `response_model.model_validate()` would return a `ResponseModel` instance,
            # which is not compatible with the generic type hint.
            validated_response: Final = TypeAdapter(response_model).validate_python(response.json())
        except JSONDecodeError as e:
            msg: Final = f"Failed to decode JSON response: {e}"
            raise UnexpectedResponse(response, msg) from e
        except ValidationError as e:
            msg: Final = f"Response from did not match expected model {response_model.__name__}: {e}"
            raise UnexpectedResponse(response, msg) from e

        return validated_response

    @staticmethod
    def _is_upper_snake_case(name: str) -> bool:
        """
        Checks if the provided name is in upper snake case format.
        :param name: The name to check.
        :return: True if the name is in upper snake case format, False otherwise.
        """
        return Client._UPPER_SNAKE_CASE_PATTERN.fullmatch(name) is not None

    def _get_auth_token(self) -> AuthToken:
        """
        Retrieves the authentication token for the client. If the token is not
        available or has expired, it will be obtained using the `_obtain_auth_token()`.
        If that fails, an exception will be raised.
        :return: The authentication token.
        :raises CommunicationError: If there is a communication error while obtaining the token.
        :raises AuthenticationError: If the authentication process fails.
        """
        if self._auth_token is None or not Client._is_token_valid(self._auth_token):
            self._auth_token = self._obtain_auth_token()
        return self._auth_token

    def _obtain_auth_token(self) -> AuthToken:
        """
        Obtains an access token for the client. This function should not be called
        directly. Instead, use the `_get_auth_token()` method to retrieve the
        access token, which will automatically handle caching and expiration.
        :return: The obtained `AuthToken`.
        :raises AuthenticationError: If the authentication process fails.
        """
        try:
            auth_response: Final = self._send_post_request(
                Endpoint.AUTH_TOKEN,
                payload=AuthRequest(
                    client_id=self._client_id,
                    client_secret=self._client_secret,
                ),
                content_type=ContentType.X_WWW_FORM_URL_ENCODED,
                response_model=AuthResponse,
                omit_authentication=True,
            )
        except UnexpectedResponse as e:
            error_response: Final = Client._validate_response(
                e.response,
                AuthErrorResponse,
                expected_status_code=HTTPStatus.BAD_REQUEST,
            )
            raise AuthenticationError(error_response) from e
        except CommunicationError as e:
            raise AuthenticationError() from e

        return AuthToken.from_auth_response(auth_response)

    @staticmethod
    def _is_token_valid(token: AuthToken) -> bool:
        """
        Checks if the provided token is valid. A token is considered valid if it is
        not None and has not expired.
        :param token: The authentication token to check.
        :return: True if the token is valid, False otherwise.
        """
        expiration_time: Final = token.expires_at - timedelta(seconds=Client._TOKEN_EXPIRATION_MARGIN_SECONDS)
        return datetime.now() < expiration_time

    def _get_endpoint_url(self, endpoint: Endpoint) -> str:
        """
        Constructs the full URL for the given endpoint.
        :param endpoint: The endpoint for which to construct the URL.
        :return: The full URL for the endpoint.
        """
        return f"{self._base_url}{endpoint.value}"
