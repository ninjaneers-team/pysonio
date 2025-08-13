from datetime import datetime
from typing import Annotated
from typing import Any
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field

# Where possible, we try to use the V2 API, but some endpoints are only available in V1.
# The topmost classes in this file are for the V2 API, while the bottommost classes are
# for the V1 API.


@final
class Error(BaseModel):
    title: str
    detail: str
    type: Optional[str] = None  # URI
    meta: Annotated[Optional[dict[str, Any]], Field(default=None, alias="_meta")]


@final
class ErrorResponse(BaseModel):
    personio_trace_id: str
    timestamp: datetime
    errors: list[Error]


@final
class V1Error(BaseModel):
    code: int
    message: str


@final
class V1ErrorResponse(BaseModel):
    success: bool
    error: V1Error
