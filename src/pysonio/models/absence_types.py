from enum import StrEnum
from typing import Annotated
from typing import Any
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


@final
class ListAbsenceTypesRequest(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/get_v2-absence-types
    """

    cursor: Optional[str] = None  # Returns first page if not provided.
    limit: Optional[int] = None  # Defaults to 100 if not provided.


@final
class AbsenceTypesUnit(StrEnum):
    DAY = "DAY"
    HOUR = "HOUR"


@final
class AbsenceTypesData(BaseModel):
    id: str
    name: str
    category: str
    unit: AbsenceTypesUnit


@final
class ListAbsenceTypesResponseMeta(BaseModel):
    # According to https://developer.personio.de/reference/get_v2-absence-types,
    # the `_meta` field contains arbitrary key/value pairs. We use `extra="allow"`
    # to allow any additional fields. But also, it is specified that the `links`
    # field must be present and must be a dictionary with string keys. For this,
    # we use a custom validator.
    model_config = ConfigDict(extra="allow")

    __pydantic_extra__: dict[str, Any] = Field(init=False)

    links: dict[str, Any]

    @field_validator("links", mode="before")
    def ensure_links_exists(cls, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise TypeError("'links' must be a dict")
        if not all(isinstance(key, str) for key in value.keys()):
            raise TypeError("All keys in 'links' must be strings")
        return value


@final
class ListAbsenceTypesResponse(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/get_v2-absence-types
    """

    data: Annotated[list[AbsenceTypesData], Field(alias="_data")]
    meta: Annotated[Optional[ListAbsenceTypesResponseMeta], Field(default=None, alias="_meta")]
