from typing import Annotated
from typing import Optional
from typing import final

from pydantic import BaseModel
from pydantic import Field


@final
class PaginationQueryParams(BaseModel):
    limit: Optional[int] = None
    cursor: Optional[str] = None


@final
class PaginationLink(BaseModel):
    href: str


@final
class PaginationLinks(BaseModel):
    # We're only interested in the `next` link for pagination.
    next: PaginationLink


@final
class PaginationMeta(BaseModel):
    """
    This is the necessary metadata for pagination. If the meta field of a response
    doesn't contain this, it is either not paginated or the pagination already ended.
    """

    links: PaginationLinks


@final
class PaginatedResponse(BaseModel):
    meta: Annotated[PaginationMeta, Field(alias="_meta")]
