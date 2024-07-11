import abc
import re
from typing import Any

import core
import utils
from icecream import ic

from message_broker import configurations

__all__ = ["Broker"]


class Broker(abc.ABC):
    config: configurations.BrokerConfig

    def __init__(
        self,
        config: dict[str, Any] | configurations.BrokerConfig = None,
        *args,
        **kwargs,
    ) -> None:
        config = config or utils.get_config()["message_broker"]
        if isinstance(config, dict):
            config = configurations.BrokerConfig(**config)
        self.config = config

    def publish_event(self, *args, **kwargs) -> None:
        raise NotImplementedError

    def group_consume(
        self,
        streams: list[str],
        group: str,
        count: int = 1,
        *args,
        **kwargs,
    ) -> core.Event:
        raise NotImplementedError

    def create_client(self, *args, **kwargs) -> str:
        raise NotImplementedError

    def get_event_stream(self, event: core.Event) -> str:
        return self.get_event_stream_from_cls(event.__class__)

    def get_event_stream_from_cls(self, event_cls: type[core.Event]) -> str:
        event_cls_name = event_cls.__name__
        snake_case = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", event_cls_name)
        stream = re.sub("([a-z0-9])([A-Z])", r"\1_\2", snake_case).lower()
        return stream
