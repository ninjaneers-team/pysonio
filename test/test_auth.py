from datetime import datetime
from datetime import timedelta
from typing import Final

import pytest

from pysonio import AuthenticationError
from pysonio import AuthToken
from pysonio import Client
from pysonio import is_token_valid
from pysonio.models.authentication import OAuth2ErrorType


def test_invalid_credentials_raises_authentication_error() -> None:
    client: Final = Client(
        client_id="invalid_client_id",
        client_secret="invalid_client_secret",
        personio_partner_identifier="SOME_PARTNER_ID",
        personio_app_identifier="SOME_APP_ID",
    )

    with pytest.raises(AuthenticationError) as exception_info:
        _ = client._get_auth_token()

    assert exception_info.value.error_response is not None
    assert exception_info.value.error_response.error == OAuth2ErrorType.INVALID_CLIENT
    assert exception_info.value.error_response.error_description == (
        "Client authentication failed (e.g., unknown client, wrong secret, no client authentication "
        + "included, or unsupported authentication method)."
    )


def test_valid_credentials_returns_valid_auth_token(client: Client) -> None:
    auth_token: Final = client._get_auth_token()
    assert is_token_valid(auth_token)


def test_auth_token_is_cached(client: Client) -> None:
    auth_token1: Final = client._get_auth_token()
    auth_token2: Final = client._get_auth_token()
    assert auth_token1 == auth_token2
    assert is_token_valid(auth_token1)
    assert is_token_valid(auth_token2)


def test_auth_token_expires_and_is_refreshed(client: Client) -> None:
    auth_token: Final = client._get_auth_token()
    assert is_token_valid(auth_token)

    # Simulate token expiration by setting the expiration time to the past.
    client._auth_token = AuthToken(
        access_token=auth_token.access_token,
        refresh_token=auth_token.refresh_token,
        expires_at=datetime.now() - timedelta(seconds=60),
        scopes=auth_token.scopes,
    )

    # The next call should refresh the token.
    new_auth_token: Final = client._get_auth_token()
    assert new_auth_token != auth_token
    assert is_token_valid(new_auth_token)
