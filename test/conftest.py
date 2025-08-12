import os
from typing import Final

import pytest
from dotenv import load_dotenv

from pysonio import Client

load_dotenv()


def get_environment_variable_or_raise(key: str) -> str:
    value: Final = os.getenv(key)
    if value is None:
        raise ValueError(f"Environment variable '{key}' is not set.")
    return value


CLIENT_ID = get_environment_variable_or_raise("CLIENT_ID")
CLIENT_SECRET = get_environment_variable_or_raise("CLIENT_SECRET")
PARTNER_ID = get_environment_variable_or_raise("PARTNER_ID")
APP_ID = get_environment_variable_or_raise("APP_ID")


@pytest.fixture
def client() -> Client:
    return Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        personio_partner_identifier=PARTNER_ID,
        personio_app_identifier=APP_ID,
    )
