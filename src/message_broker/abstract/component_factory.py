import abc
from typing import Any
import utils
from message_broker import configurations
from message_broker.abstract.broker import Broker as AbstractBroker

__all__ = ["ComponentFactory"]


class ComponentFactory(abc.ABC):
    def __init__(
        self,
        config: dict[str, Any] = None,
        *args,
        **kwargs,
    ) -> None:
        """ """
        if config is None:
            config = utils.get_config().get("message_broker", {})
        if isinstance(config, dict):
            config = configurations.BrokerConfig(**config)
        self.config = config

    @abc.abstractmethod
    def create_broker(self, *args, **kwargs) -> AbstractBroker:
        """ """
        raise NotImplementedError
