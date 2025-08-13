from datetime import datetime
from enum import StrEnum
from typing import Annotated
from typing import Final
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field

from pysonio.filters import DateRangeFilter
from pysonio.filters import RangeFilterOperator
from pysonio.models.meta import MetaWithLinks


@final
class ListAbsencePeriodsQueryParams(BaseModel):
    limit: Optional[int] = None
    cursor: Optional[str] = None
    id: Optional[str] = None
    absence_type_id: Annotated[Optional[str], Field(default=None, alias="absence_type.id")]
    person_id: Annotated[Optional[str], Field(default=None, alias="person.id")]
    starts_from_date_time_gte: Annotated[Optional[datetime], Field(default=None, alias="starts_from.date_time.gte")]
    starts_from_date_time_lte: Annotated[Optional[datetime], Field(default=None, alias="starts_from.date_time.lte")]
    ends_at_date_time_gte: Annotated[Optional[datetime], Field(default=None, alias="ends_from.date_time.gte")]
    ends_at_date_time_lte: Annotated[Optional[datetime], Field(default=None, alias="ends_from.date_time.lte")]
    updated_at_gte: Annotated[Optional[datetime], Field(default=None, alias="updated_at.gte")]
    updated_at_lte: Annotated[Optional[datetime], Field(default=None, alias="updated_at.lte")]

    @classmethod
    def from_params(
        cls,
        *,
        limit: Optional[int] = None,
        id_: Optional[str] = None,
        absence_type_id: Optional[str] = None,
        person_id: Optional[str] = None,
        starts_from_filters: Optional[list[DateRangeFilter]] = None,
        end_at_filters: Optional[list[DateRangeFilter]] = None,
        updated_at_filters: Optional[list[DateRangeFilter]] = None,
    ):
        params: Final = cls(
            limit=limit,
            id=id_,
            # Aliased fields cannot be populated directly, so we use dict unpacking.
            **({"absence_type.id": absence_type_id} if absence_type_id is not None else {}),
            **({"person.id": person_id} if person_id is not None else {}),
            # Placeholders to satisfy type checker.
            starts_from_date_time_gte=None,
            starts_from_date_time_lte=None,
            ends_at_date_time_gte=None,
            ends_at_date_time_lte=None,
            updated_at_gte=None,
            updated_at_lte=None,
        )
        if starts_from_filters is not None:
            for filter_ in starts_from_filters:
                match filter_.operator:
                    case RangeFilterOperator.LESS_THAN_OR_EQUAL:
                        params.starts_from_date_time_lte = filter_.value
                    case RangeFilterOperator.GREATER_THAN_OR_EQUAL:
                        params.starts_from_date_time_gte = filter_.value
        if end_at_filters is not None:
            for filter_ in end_at_filters:
                match filter_.operator:
                    case RangeFilterOperator.LESS_THAN_OR_EQUAL:
                        params.ends_at_date_time_lte = filter_.value
                    case RangeFilterOperator.GREATER_THAN_OR_EQUAL:
                        params.ends_at_date_time_gte = filter_.value
        if updated_at_filters is not None:
            for filter_ in updated_at_filters:
                match filter_.operator:
                    case RangeFilterOperator.LESS_THAN_OR_EQUAL:
                        params.updated_at_lte = filter_.value
                    case RangeFilterOperator.GREATER_THAN_OR_EQUAL:
                        params.updated_at_gte = filter_.value
        return params


@final
class DateType(StrEnum):
    FIRST_HALF = "FIRST_HALF"
    SECOND_HALF = "SECOND_HALF"


@final
class Person(BaseModel):
    id: str


@final
class StartsFrom(BaseModel):
    date_time: datetime
    type: Optional[DateType] = DateType.FIRST_HALF


@final
class EndsAt(BaseModel):
    date_time: datetime
    type: Optional[DateType] = DateType.SECOND_HALF


@final
class AbsenceType(BaseModel):
    id: str


@final
class AbsencePeriodData(BaseModel):
    id: str
    person: Person
    starts_from: StartsFrom
    ends_at: Optional[EndsAt] = None
    comment: Optional[str] = None
    absence_type: AbsenceType
    created_at: datetime
    updated_at: datetime


@final
class ListAbsencePeriodsResponse(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/get_v2-absence-periods-id
    """

    data: Annotated[list[AbsencePeriodData], Field(alias="_data")]
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]


@final
class CreateAbsencePeriodQueryParams(BaseModel):
    skip_approval: Optional[bool] = None  # Defaults to `False` if not provided.


@final
class CreateAbsencePeriodRequest(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/post_v2-absence-periods
    """

    person: Person
    starts_from: StartsFrom
    ends_at: Optional[EndsAt] = None
    comment: Optional[str] = None
    absence_type: AbsenceType


@final
class CreateAbsencePeriodResponse(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/post_v2-absence-periods
    """

    id: str
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]


@final
class ApprovalStatus(StrEnum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DELETION_PENDING = "DELETION_PENDING"
    SUBSTITUTE_REQUESTED = "SUBSTITUTE_REQUESTED"


@final
class Approval(BaseModel):
    status: ApprovalStatus
