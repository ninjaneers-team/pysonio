from datetime import datetime
from typing import Annotated
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field

from pysonio.models.meta import MetaWithLinks


@final
class RetrieveOrgUnitQueryParams(BaseModel):
    type: str  # E.g., team or department.
    include_parent_chain: Optional[bool] = None  # Defaults to `False` if not provided.


@final
class OrgUnitParent(BaseModel):
    id: str
    type: str
    name: str
    resource_uri: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    create_time: datetime
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]


@final
class RetrieveOrgUnitResponse(BaseModel):
    id: str
    type: str
    name: str
    resource_uri: Optional[str] = None
    abbreviation: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[str] = None
    create_time: datetime
    parent_chain: Optional[list[OrgUnitParent]] = None
    meta: Annotated[Optional[MetaWithLinks], Field(default=None, alias="_meta")]
