from datetime import datetime
from enum import StrEnum
from typing import Annotated
from typing import Optional
from typing import Self
from typing import final

from pydantic import BaseModel
from pydantic import Field

from pysonio import DateFilter
from pysonio.filters import Operator
from pysonio.models.meta import MetaWithLinks


@final
class ListPersonsQueryParams(BaseModel):
    """
    Modelled after https://developer.personio.de/reference/get_v2-persons
    """

    limit: Annotated[Optional[int], Field(default=None, ge=1, le=50)]  # Defaults to 10.
    cursor: Optional[str] = None
    id: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    preferred_name: Optional[str] = None
    created_at: Optional[datetime] = None
    created_at_gt: Annotated[Optional[datetime], Field(default=None, alias="created_at.gt")]
    created_at_lt: Annotated[Optional[datetime], Field(default=None, alias="created_at.lt")]
    updated_at: Optional[datetime] = None
    updated_at_gt: Annotated[Optional[datetime], Field(default=None, alias="updated_at.gt")]
    updated_at_lt: Annotated[Optional[datetime], Field(default=None, alias="updated_at.lt")]

    @classmethod
    def from_params(
        cls,
        *,
        limit: Optional[int] = None,
        id_: Optional[str] = None,
        email: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        preferred_name: Optional[str] = None,
        created_at_filters: Optional[list[DateFilter]] = None,
        updated_at_filters: Optional[list[DateFilter]] = None,
    ) -> Self:
        result = cls(
            limit=limit,
            id=id_,
            email=email,
            first_name=first_name,
            last_name=last_name,
            preferred_name=preferred_name,
            # Placeholders to satisfy type checker.
            created_at=None,
            created_at_gt=None,
            created_at_lt=None,
            updated_at=None,
            updated_at_gt=None,
            updated_at_lt=None,
        )
        if created_at_filters is not None:
            for filter_ in created_at_filters:
                match filter_.operator:
                    case Operator.EQUALS:
                        result.created_at = filter_.value
                    case Operator.LESS_THAN:
                        result.created_at_lt = filter_.value
                    case Operator.GREATER_THAN:
                        result.created_at_gt = filter_.value
        if updated_at_filters is not None:
            for filter_ in updated_at_filters:
                match filter_.operator:
                    case Operator.EQUALS:
                        result.updated_at = filter_.value
                    case Operator.LESS_THAN:
                        result.updated_at_lt = filter_.value
                    case Operator.GREATER_THAN:
                        result.updated_at_gt = filter_.value
        return result


@final
class Gender(StrEnum):
    UNSPECIFIED = "UNSPECIFIED"
    MALE = "MALE"
    FEMALE = "FEMALE"
    DIVERSE = "DIVERSE"


@final
class ProfilePicture(BaseModel):
    url: str


@final
class PersonStatus(StrEnum):
    UNSPECIFIED = "UNSPECIFIED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# Contradicting the documentation (see https://developer.personio.de/reference/get_v2-persons),
# the `type` field is sent in lowercase.
@final
class CustomAttributeType(StrEnum):
    UNSPECIFIED = "unspecified"
    STRING = "string"
    INT = "int"
    DOUBLE = "double"
    DATE = "date"
    BOOLEAN = "boolean"
    STRING_LIST = "string_list"


@final
class CustomAttribute(BaseModel):
    id: str
    type: CustomAttributeType
    global_id: str
    label: Optional[str] = None
    value: str | list[str] | list[dict]


@final
class Employment(BaseModel):
    id: str


@final
class PersonData(BaseModel):
    id: str
    email: str
    created_at: Optional[datetime] = None
    updated_at: datetime
    first_name: str
    last_name: str
    preferred_name: str
    gender: Optional[Gender] = None
    profile_picture: ProfilePicture
    status: PersonStatus
    custom_attributes: Optional[list[CustomAttribute]] = None
    employments: list[Employment]


@final
class ListPersonsResponse(BaseModel):
    """
    Modelled after https://developer.personio.de/reference/get_v2-persons
    """

    data: Annotated[list[PersonData], Field(alias="_data")]
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]
