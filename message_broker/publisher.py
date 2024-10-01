import logging
from typing import Any
from message_broker import abstract
from message_broker import mixin
from message_broker.types import Broker
import core

logger = logging.getLogger(__file__)


class Publisher(mixin.Mixin):
    streams: list[str]
    broker: Broker

    def __init__(
        self,
        config: dict[str, Any] = None,
    ) -> None:
        super().__init__(config)

    def publish(self, event: core.Event) -> Any:
        response = self.broker.publish_event(event)
        return response
