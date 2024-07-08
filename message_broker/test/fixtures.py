from typing import Any, Generator
import uuid
import pydantic
import pytest
import redis
from icecream import ic
from message_broker import consumer as message_consumer
from message_broker import publisher as message_publisher
from message_broker.adapters import redis_adapter


@pytest.fixture(scope="session")
def streams() -> Generator[list[str], Any, None]:
    yield []


@pytest.fixture
def consumer() -> Generator[message_consumer.Consumer, Any, None]:
    consumer_ = message_consumer.Consumer()
    yield consumer_


@pytest.fixture
def publisher() -> Generator[message_publisher.Publisher, Any, None]:
    publisher_ = message_publisher.Publisher()
    yield publisher_


@pytest.fixture(scope="session")
def redis_group_consumer() -> Generator[str, Any, None]:
    group = str(uuid.uuid4())
    yield group


class CleanupConfig(pydantic.BaseModel):
    enable: bool = False
    before: bool = False
    after: bool = False


class TestConfig(pydantic.BaseModel):
    __test__ = False

    cleanup: CleanupConfig = pydantic.Field(default_factory=lambda: CleanupConfig)


@pytest.fixture(scope="session")
def message_broker_test_config() -> Generator[TestConfig, Any, None]:
    config = TestConfig(
        cleanup=CleanupConfig(
            enable=False,
            before=False,
            after=False,
        )
    )
    yield config


def cleanup_broker(
    broker: redis_adapter.Broker,
    streams: dict[str, str],
):
    broker.client.delete(*list(streams.keys()))
    for stream, group in streams.items():
        try:
            broker.client.xgroup_destroy(name=stream, groupname=group)
        except redis.exceptions.ResponseError as e:
            message = str(e)
            if "requires the key to exist" in message:
                continue


@pytest.fixture
def redis_broker(
    consumer: message_consumer.Consumer,
    redis_group_consumer: str,
    streams: list[str] | dict[str, str],
    message_broker_test_config: TestConfig,
) -> Generator[redis_adapter.Broker, Any, None]:
    broker_ = consumer.broker
    broker_.streams = {}
    group = redis_group_consumer
    config = message_broker_test_config

    # Cleanup streams before testing
    if config.cleanup.enable and config.cleanup.before:
        cleanup_broker(broker=broker_, streams=streams)
        ic("Cleanup before testing")

    if isinstance(streams, list):
        streams = {stream: group for stream in streams}

    for stream, defined_group in streams.items():
        if defined_group is None:
            streams[stream] = group

    for stream, group in streams.items():
        broker_.streams[stream] = group
        try:
            broker_.client.xgroup_create(stream, group, mkstream=True)
        except redis.exceptions.ResponseError as e:
            message = str(e)
            if "Consumer Group name already exists" in message:
                continue

    yield broker_

    # Cleanup streams after testing
    if config.cleanup.enable and config.cleanup.after:
        cleanup_broker(broker=broker_, streams=streams)
        ic("Cleanup after testing")
