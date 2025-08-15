from enum import Enum
from typing import final


@final
class Endpoint(Enum):
    AUTH_TOKEN = "/v2/auth/token"
    ABSENCE_TYPES = "/v2/absence-types"
    ABSENCE_PERIODS = "/v2/absence-periods"
    PERSONS = "/v2/persons"
    EMPLOYEES = "/v1/company/employees"
    ORG_UNITS = "/v2/org-units"
