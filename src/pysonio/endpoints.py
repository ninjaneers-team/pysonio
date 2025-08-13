from enum import Enum
from typing import final


@final
class Endpoint(Enum):
    AUTH_TOKEN = "/v2/auth/token"
    ABSENCE_TYPES = "/v2/absence-types"
    PERSONS = "/v2/persons"
    EMPLOYEES = "/v1/company/employees"
