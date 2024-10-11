import pathlib
from typing import Any, Generator

import core
import pytest
import utils
from icecream import ic

import message_broker


@pytest.fixture(scope="session")
def project_path() -> pathlib.Path:
    yield pathlib.Path(__file__).parents[2]


@pytest.fixture(scope="session")
def config_path(project_path: pathlib.Path) -> Generator[str, Any, None]:
    yield str(project_path / ".configs")


@pytest.fixture(scope="session")
def config(config_path: str):
    yield utils.load_config(config_path)


@pytest.fixture
def redis_broker(
    config: dict[str, Any]
) -> Generator[message_broker.RedisBroker, Any, None]:
    yield message_broker.RedisBroker(config=config["message_broker"])


def test_broker(redis_broker: message_broker.RedisBroker):
    class TestEvent(core.Event):
        __test__ = False

        a: str

    ic(redis_broker.publish_event(TestEvent(a="4")))
    messages = redis_broker.group_consume(["test_event"])
    ic(messages)
