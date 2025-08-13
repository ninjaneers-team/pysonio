from typing import Annotated
from typing import Literal
from typing import final

from pydantic import BaseModel
from pydantic import Field


@final
class GetAbsenceBalanceQueryParams(BaseModel):
    employee_id: Annotated[int, Field(ge=0, le=2**31 - 1)]


@final
class AbsenceBalanceData(BaseModel):
    id: int
    name: str
    category: str
    # Practical tests have shown that both `balance` and `available_balance` can be non-integer values,
    # e.g. for half days or even smaller fractions of a day (e.g. `8.33`).
    balance: float
    available_balance: float


@final
class GetAbsenceBalanceResponse(BaseModel):
    """
    Modelled after:
    https://developer.personio.de/v1.0/reference/get_company-employees-employee-id-absences-balance
    """

    success: Literal[True]
    data: list[AbsenceBalanceData]
