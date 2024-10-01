from typing import Any

import utils

from message_broker import abstract, adapters, configurations
from message_broker.types import Broker, ComponentFactory


class Mixin:
    component_factory: ComponentFactory
    broker: Broker

    def __init__(self, config: dict[str, Any] | configurations.BrokerConfig = None):
        config = config or utils.get_config().get(
            "message_broker",
            {},
        )
        config = (
            configurations.BrokerConfig(**config)
            if isinstance(config, dict)
            else config
        )

        self.config = config
        self.component_factory = self.__init_component_factory()
        self.broker = self.component_factory.create_broker()
        self.default_group = self.broker.default_group
        self.streams = self.broker.streams

    @property
    def broker(self) -> Broker:
        return self._broker

    @broker.setter
    def broker(self, new_broker: Broker) -> None:
        if not isinstance(new_broker, abstract.Broker):
            raise TypeError(f"Expected Broker, got {type(new_broker)}")
        self._broker = new_broker

    def __init_component_factory(self) -> abstract.ComponentFactory:
        return adapters.adapter_routers[self.config.framework](config=self.config)
