from typing import Final
from typing import Optional
from typing import final

import requests

from pysonio.models.authentication import AuthErrorResponse
from pysonio.models.authentication import OAuth2ErrorType
from pysonio.models.error_response import ErrorResponse
from pysonio.models.error_response import V1ErrorResponse


class PysonioError(Exception):
    """
    Base class for all exceptions raised by the Pysonio library.

    This class serves as the base for all exceptions that can be raised by the library,
    allowing for a consistent error handling mechanism.
    """


class CommunicationError(PysonioError):
    """
    Exception raised when a communication error occurs.

    This exception is raised when there is an issue with the communication between the client
    and the Personio API, such as network errors, timeouts, or invalid responses.
    """


@final
class AuthenticationError(PysonioError):
    """
    Exception raised when an authentication error occurs.

    This exception is raised when the authentication process fails due to various reasons,
    such as invalid credentials, unsupported grant types, or server errors.
    It encapsulates the error response received from the authentication service.
    """

    def __init__(self, error_response: Optional[AuthErrorResponse] = None) -> None:
        """
        Exception raised when an authentication error occurs.
        :param error_response: The error response containing details about the authentication error (if available).
        """
        super().__init__(
            "Unknown authentication error occurred."
            if error_response is None
            else AuthenticationError._get_error_message(error_response.error)
        )
        self._error_response: Final = error_response

    @property
    def error_response(self) -> Optional[AuthErrorResponse]:
        """Returns the error response that caused this exception or None if not available."""
        return self._error_response

    @staticmethod
    def _get_error_message(error_type: OAuth2ErrorType) -> str:
        match error_type:
            case OAuth2ErrorType.INVALID_REQUEST:
                return "The request is invalid."
            case OAuth2ErrorType.INVALID_CLIENT:
                return "The client credentials are invalid."
            case OAuth2ErrorType.INVALID_GRANT:
                return "The provided grant is invalid."
            case OAuth2ErrorType.UNAUTHORIZED_CLIENT:
                return "The client is not authorized to request an access token."
            case OAuth2ErrorType.UNSUPPORTED_GRANT_TYPE:
                return "The grant type is not supported."
            case OAuth2ErrorType.INVALID_SCOPE:
                return "The requested scope is invalid."
            case OAuth2ErrorType.SERVER_ERROR:
                return "An internal server error occurred."
            case OAuth2ErrorType.TEMPORARILY_UNAVAILABLE:
                return "The service is temporarily unavailable."
            case OAuth2ErrorType.ACCESS_DENIED:
                return "Access to the resource is denied."
            case OAuth2ErrorType.UNSUPPORTED_RESPONSE_TYPE:
                return "The response type is not supported."
            case _:
                # Pyrefly has a bug where it doesn't recognize that the match statement
                # is exhaustive. See:
                # https://github.com/facebook/pyrefly/issues/400#issuecomment-3173377989
                raise RuntimeError("Unreachable")


@final
class UnexpectedResponse(CommunicationError):
    """
    Wrapper around a `requests.Response` object that indicates an unexpected response. This
    is just to make it clear that the response is not what was expected.
    """

    def __init__(self, response: requests.Response, message: str) -> None:
        super().__init__(f"Unexpected response: {message}")
        self._response: Final = response

    @property
    def response(self) -> requests.Response:
        """Returns the unexpected response that caused this exception."""
        return self._response


@final
class BadRequestError(CommunicationError):
    def __init__(self, error_response: ErrorResponse, message: str) -> None:
        """
        Exception raised when a bad request error occurs.

        :param error_response: The error response containing details about the bad request.
        :param message: A message describing the error.
        """
        super().__init__(f"400 Bad request: {message}")
        self._error_response: Final = error_response

    @property
    def error_response(self) -> ErrorResponse:
        """Returns the error response that caused this exception."""
        return self._error_response


@final
class ForbiddenError(CommunicationError):
    def __init__(self, error_response: ErrorResponse, message: str) -> None:
        """
        Exception raised when a forbidden error occurs. This can be caused by insufficient scopes.

        :param error_response: The error response containing details about the forbidden request.
        :param message: A message describing the error.
        """
        super().__init__(f"403 Forbidden: {message}")
        self._error_response: Final = error_response

    @property
    def error_response(self) -> ErrorResponse:
        """Returns the error response that caused this exception."""
        return self._error_response


@final
class UnprocessableContentError(CommunicationError):
    def __init__(self, error_response: ErrorResponse, message: str) -> None:
        """
        Exception raised when an unprocessable content error occurs.

        :param error_response: The error response containing details about the unprocessable content.
        :param message: A message describing the error.
        """
        super().__init__(f"422 Unprocessable Content: {message}")
        self._error_response: Final = error_response

    @property
    def error_response(self) -> ErrorResponse:
        """Returns the error response that caused this exception."""
        return self._error_response


@final
class NotFoundError(CommunicationError):
    def __init__(
        self,
        error_response: V1ErrorResponse | ErrorResponse,
        message: str,
    ) -> None:
        """
        Exception raised when a not found error occurs.

        :param error_response: The error response containing details about the not found request.
        :param message: A message describing the error.
        """
        super().__init__(f"404 Not Found: {message}")
        self._error_response: Final = error_response

    @property
    def error_response(self) -> V1ErrorResponse | ErrorResponse:
        """Returns the error response that caused this exception."""
        return self._error_response
