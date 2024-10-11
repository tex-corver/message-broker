from message_broker import abstract
from typing import TypeVar

ComponentFactory = TypeVar("ComponentFactory", bound=abstract.ComponentFactory)
Broker = TypeVar("Broker", bound=abstract.Broker)
