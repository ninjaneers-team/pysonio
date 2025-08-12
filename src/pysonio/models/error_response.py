from datetime import datetime
from typing import Annotated
from typing import Any
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field


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
