import logging
from message_broker import configurations, mixin
from message_broker.types import Broker
import core

logger = logging.getLogger(__file__)


class ConsumerStream:
    stream: str
    group: str


class Consumer(mixin.Mixin):
    broker: Broker
    streams: dict[str, str]
    default_group: str
    config: configurations.BrokerConfig

    def __init__(self, config: dict[str, str] = None) -> None:
        super().__init__(config)

    def add_stream(self, stream: str, group: str = None, *args, **kwargs):
        if stream in self.streams:
            logger.warning(f"Stream {stream} already in consumer stream list.")

        self.streams[stream] = group

    def group_consume(
        self,
        streams: list[str] = None,
        group: str = None,
        count: int = 1,
        **kwargs,
    ):
        return self.broker.group_consume(
            streams=self.streams, group=self.default_group, count=count, **kwargs
        )

    def consume_event_from_stream(
        self, stream: str, *args, **kwargs
    ) -> core.Event | None:
        group = self.streams[stream]
        event = self.broker.group_consume(stream, group, *args, **kwargs)
        return event
