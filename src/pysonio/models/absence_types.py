from enum import StrEnum
from typing import Annotated
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field

from pysonio.models.meta import MetaWithLinks


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
class ListAbsenceTypesResponse(BaseModel):
    """
    Modelled after: https://developer.personio.de/reference/get_v2-absence-types
    """

    data: Annotated[list[AbsenceTypesData], Field(alias="_data")]
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]
