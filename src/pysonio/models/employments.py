from datetime import date
from datetime import datetime
from enum import StrEnum
from typing import Annotated
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field

from pysonio import Person
from pysonio.models.meta import MetaWithLinks


@final
class Position(BaseModel):
    title: str


@final
class EmploymentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    ONBOARDING = "ONBOARDING"
    LEAVE = "LEAVE"
    UNSPECIFIED = "UNSPECIFIED"


@final
class EmploymentType(StrEnum):
    UNSPECIFIED = "UNSPECIFIED"
    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"


@final
class Supervisor(BaseModel):
    id: str


@final
class Office(BaseModel):
    id: str


@final
class OrgUnit(BaseModel):
    type: str  # E.g., team or department.
    id: str


@final
class TerminationType(StrEnum):
    UNSPECIFIED = "UNSPECIFIED"
    EMPLOYEE = "EMPLOYEE"
    FIRED = "FIRED"
    DEATH = "DEATH"
    CONTRACT_EXPIRED = "CONTRACT_EXPIRED"
    AGREEMENT = "AGREEMENT"
    SUB_COMPANY_SWITCH = "SUB_COMPANY_SWITCH"
    IRREVOCABLE_SUSPENSION = "IRREVOCABLE_SUSPENSION"
    CANCELLATION = "CANCELLATION"
    COLLECTIVE_AGREEMENT = "COLLECTIVE_AGREEMENT"
    SETTLEMENT_AGREEMENT = "SETTLEMENT_AGREEMENT"
    RETIREMENT = "RETIREMENT"
    COURT_SETTLEMENT = "COURT_SETTLEMENT"
    QUIT = "QUIT"


@final
class CostCenter(BaseModel):
    id: str
    weight: float


@final
class Termination(BaseModel):
    termination_date: Optional[date] = None
    last_working_day: Optional[date] = None
    terminated_at: Optional[date] = None
    type: Optional[TerminationType] = None
    reason: Optional[str] = None


@final
class LegalEntity(BaseModel):
    id: str


@final
class SubCompany(BaseModel):
    id: str


@final
class EmploymentData(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/get_v2-persons-person-id-employments-id
    """

    id: str
    position: Position
    status: EmploymentStatus
    # The total amount of weekly working hours.
    weekly_working_hours: Optional[float] = None
    # The number of hours per week that is considered full time for the employment.
    full_time_weekly_working_hours: Optional[float] = None
    # I don't know why, but the following date values are strings instead of dates ¯\_(ツ)_/¯
    probation_end_date: str
    employment_start_date: str
    employment_end_date: Optional[str] = None
    type: Optional[EmploymentType] = None
    contract_end_date: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: datetime
    supervisor: Optional[Supervisor] = None
    office: Optional[Office] = None
    org_units: list[OrgUnit]
    person: Person
    termination: Termination
    cost_centers: Optional[list[CostCenter]] = None
    legal_entity: Optional[LegalEntity] = None
    sub_company: Optional[SubCompany] = None  # Note: Marked as deprecated.
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]
