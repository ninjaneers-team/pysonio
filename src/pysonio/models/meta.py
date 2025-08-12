from typing import Any
from typing import final

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field
from pydantic import field_validator


@final
class MetaWithLinks(BaseModel):
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
