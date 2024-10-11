__all__ = [
    "ConsumerConfig",
    "BrokerConfig",
    "BrokerConnectionConfig",
]

import os
from typing import Any, Optional

import pydantic


class ConsumerConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    default_group: Optional[str] = os.environ.get("SERVICE", "unknown")
    name: Optional[str] = os.environ.get("INSTANCE_ID", "unknown")
    streams: Optional[dict[str, Any]] = pydantic.Field(default_factory=dict)


class BrokerConnectionConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    host: Optional[str] = "localhost"
    port: Optional[int] = 6379
    username: Optional[str] | None = None
    password: Optional[str] | None = None
    ssl: Optional[bool] = False
    db: Optional[int] = 0


class BrokerConfig(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(extra="allow")

    framework: Optional[str] = "redis"
    connection: Optional[BrokerConnectionConfig] = pydantic.Field(
        default_factory=BrokerConnectionConfig
    )
    args: dict[str, Any] = pydantic.Field(default_factory=dict)
    consumer: Optional[ConsumerConfig] = pydantic.Field(default_factory=ConsumerConfig)
