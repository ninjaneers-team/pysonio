from enum import Enum
from typing import final


@final
class Endpoint(Enum):
    AUTH_TOKEN = "/v2/auth/token"
