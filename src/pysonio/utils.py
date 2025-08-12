import re
import urllib.parse
from datetime import datetime
from datetime import timedelta
from typing import Final

from pysonio import AuthToken

_TOKEN_EXPIRATION_MARGIN_SECONDS = 3 * 60  # 3 minutes
_UPPER_SNAKE_CASE_PATTERN = re.compile(r"^[A-Z0-9]+(?:_[A-Z0-9]+)*$")


def is_token_valid(token: AuthToken) -> bool:
    """
    Checks if the provided token is valid. A token is considered valid if it is
    not None and has not expired.
    :param token: The authentication token to check.
    :return: True if the token is valid, False otherwise.
    """
    expiration_time: Final = token.expires_at - timedelta(seconds=_TOKEN_EXPIRATION_MARGIN_SECONDS)
    return datetime.now() < expiration_time


def is_upper_snake_case(name: str) -> bool:
    """
    Checks if the provided name is in upper snake case format.
    :param name: The name to check.
    :return: True if the name is in upper snake case format, False otherwise.
    """
    return _UPPER_SNAKE_CASE_PATTERN.fullmatch(name) is not None


def extract_query_params(url: str) -> dict[str, str | list[str]]:
    """
    Extracts query parameters from a URL and returns them as a dictionary.
    If a query parameter has multiple values, it will be returned as a list.
    :param url: The URL from which to extract query parameters.
    :return: dict[str, str | list[str]] - A dictionary containing the query parameters.
    """
    params: Final = urllib.parse.parse_qs(urllib.parse.urlsplit(url).query, keep_blank_values=True)
    # If a query parameter has multiple values, it will be returned as a list.
    return {k: v[0] if len(v) == 1 else v for k, v in params.items()}
