from typing import Any

import core

from message_broker import abstract, configurations, mixin


class Client(mixin.Mixin):
    broker: abstract.Broker

    def __init__(self, config: dict[str, Any] | configurations.BrokerConfig) -> None:
        super().__init__(conifg=config)

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
        self.broker.group_consume(
            streams=streams,
            group=group,
            count=count,
            *args,
            **kwargs,
        )

    def create_client(self, *args, **kwargs) -> str:
        raise NotImplementedError

    def get_event_stream(self, event: core.Event) -> str:
        return self.get_event_stream_from_cls(event.__class__)
