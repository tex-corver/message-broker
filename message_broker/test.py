__test__ = False

import pytest

import message_broker
from message_broker import abstract
import core


@pytest.fixture
def clear_streams(redis_broker: message_broker.RedisBroker) -> None:
    yield
    redis_broker._clear_all_streams()


class Broker(abstract.Broker):
    __test__ = False
    """
    """

    def __init__(
        self,
        scenario: dict[tuple[str, str], core.Event],
    ):
        self.scenario = scenario

    def consume_event(self, stream: str, group: str) -> core.Event:
        return self.scenario[(stream, group)]

    def group_consume(self, stream: str, group: str) -> core.Event:
        return self.scenario[(stream, group)]


class ComponentFactory(abstract.ComponentFactory):
    def create_broker(self, *args, **kwargs) -> Broker:
        return Broker
