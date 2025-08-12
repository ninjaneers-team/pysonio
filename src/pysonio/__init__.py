import re
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
from pysonio.errors import CommunicationError
from pysonio.errors import UnexpectedResponse
from pysonio.models.authentication import AuthErrorResponse
from pysonio.models.authentication import AuthRequest
from pysonio.models.authentication import AuthResponse
from pysonio.models.authentication import AuthToken


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

    @staticmethod
    def _is_upper_snake_case(name: str) -> bool:
        return Client._UPPER_SNAKE_CASE_PATTERN.fullmatch(name) is not None

    def _obtain_auth_token(self) -> AuthToken:
        """
        Obtains an access token for the client. This function should not be called
        directly. Instead, use the `_get_auth_token()` method to retrieve the
        access token, which will automatically handle the token retrieval if it is
        not already available or has expired.
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
        """
        expiration_time: Final = token.expires_at - timedelta(seconds=Client._TOKEN_EXPIRATION_MARGIN_SECONDS)
        return datetime.now() < expiration_time

    def _get_endpoint_url(self, endpoint: Endpoint) -> str:
        return f"{self._base_url}{endpoint.value}"

    def _get_headers(
        self,
        content_type: ContentType,
        *,
        is_beta: bool,
        omit_authentication: bool,
    ) -> dict[str, str]:
        """
        Returns the headers to be used for requests to the Personio API.
        :param is_beta: Whether the request is for a beta endpoint.
        :param omit_authentication: Whether to skip authentication for the request.
        :return: A dictionary containing the headers.
        """
        headers: Final = self._personio_headers
        if is_beta:
            headers["Beta"] = "true"
        headers["Accept"] = "application/json"
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

    def _send_post_request[Payload: BaseModel, ResponseModel: BaseModel](
        self,
        endpoint: Endpoint,
        *,
        payload: Payload,
        content_type: ContentType,
        response_model: type[ResponseModel],
        expected_status_code: HTTPStatus = HTTPStatus.OK,
        is_beta: bool = False,
        omit_authentication: bool = False,
    ) -> ResponseModel:
        url: Final = self._get_endpoint_url(endpoint)
        headers: Final = self._get_headers(
            content_type,
            is_beta=is_beta,
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

        validated_response: Final = Client._validate_response(
            response,
            response_model,
            expected_status_code=expected_status_code,
        )
        return validated_response
