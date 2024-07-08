from typing import Any

import pydantic


class Header(pydantic.BaseModel):
    id: str
    stream: str
    group: str | None = None
    consumer: str | None = None


class Message(pydantic.BaseModel):
    header: Header | None = None
    body: dict[str, Any] | None = None
