from enum import Enum
from typing import final


@final
class ContentType(Enum):
    X_WWW_FORM_URL_ENCODED = "application/x-www-form-urlencoded"
    JSON = "application/json"
