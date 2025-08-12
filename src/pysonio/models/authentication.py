from datetime import datetime
from datetime import timedelta
from enum import StrEnum
from typing import Final
from typing import Literal
from typing import NamedTuple
from typing import Optional
from typing import Self
from typing import final

from pydantic import BaseModel


@final
class AuthRequest(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/post_v2-auth-token
    """

    client_id: str
    client_secret: str
    # According to the documentation, at the moment this is the only supported grant type.
    grant_type: Literal["client_credentials"] = "client_credentials"
    scope: Optional[str] = None


@final
class OAuth2ErrorType(StrEnum):
    INVALID_REQUEST = "invalid_request"
    INVALID_CLIENT = "invalid_client"
    INVALID_GRANT = "invalid_grant"
    UNAUTHORIZED_CLIENT = "unauthorized_client"
    UNSUPPORTED_GRANT_TYPE = "unsupported_grant_type"
    INVALID_SCOPE = "invalid_scope"
    SERVER_ERROR = "server_error"
    TEMPORARILY_UNAVAILABLE = "temporarily_unavailable"
    ACCESS_DENIED = "access_denied"
    UNSUPPORTED_RESPONSE_TYPE = "unsupported_response_type"


@final
class AuthErrorResponse(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/post_v2-auth-token
    """

    error: OAuth2ErrorType
    error_description: Optional[str] = None
    error_uri: Optional[str] = None
    timestamp: datetime
    trace_id: str
    meta: Optional[dict] = None


@final
class AuthResponse(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/post_v2-auth-token
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: Literal["Bearer"] = "Bearer"
    expires_in: int  # In seconds, default value is 1 day.
    scope: str  # Space delimited array of scopes assigned to the granted token.


@final
class AuthToken(NamedTuple):
    access_token: str
    refresh_token: Optional[str]
    expires_at: datetime
    scopes: list[str]

    @classmethod
    def from_auth_response(cls, response: AuthResponse) -> Self:
        """
        Creates an AuthToken instance from an AuthResponse.

        :param response: The AuthResponse to create the AuthToken from.
        :return: An instance of AuthToken.
        """
        expires_at: Final = datetime.now() + timedelta(seconds=response.expires_in)
        scopes: Final = response.scope.split() if response.scope else []
        return cls(
            access_token=response.access_token,
            refresh_token=response.refresh_token,
            expires_at=expires_at,
            scopes=scopes,
        )
