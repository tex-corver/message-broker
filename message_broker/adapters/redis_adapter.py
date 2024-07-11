from __future__ import annotations

import json
import os
from typing import Any, Optional

import core
import pydantic
import redis
from core.messages import Event
from icecream import ic

from message_broker import abstract, configurations
from message_broker import messages as queue_messages


class ComponentFactory(abstract.ComponentFactory):
    def __init__(self, config: dict[str, Any] = None) -> None:
        super().__init__(config)

    def create_broker(self) -> Broker:
        return Broker(self.config)


class RedisConnectionConfig(configurations.BrokerConnectionConfig):
    ssl: Optional[bool] = None
    ssl_ca_certs: Optional[str] = None
    decode_responses: Optional[bool] = None


class RedisConfig(pydantic.BaseModel):
    connection: RedisConnectionConfig
    consumer: Optional[configurations.ConsumerConfig] = pydantic.Field(
        default_factory=configurations.ConsumerConfig
    )


class StreamEvent:
    id: str
    body: ...


class GroupConsumeResponse:
    e: list


class Broker(abstract.Broker):
    config: configurations.BrokerConfig
    client: redis.Redis

    def __init__(self, config: dict[str, Any] = None) -> None:
        super().__init__(config=config)
        self.default_group = self.config.consumer.default_group or "unknown"
        self.streams = self.__init_consumer_streams()
        self.client = self.create_client()
        self.__init_consumer_group()
        self.name = self.get_name()

    def get_name(self) -> str:
        name = self.config.consumer.name
        if name is not None:
            return name
        return os.environ.get("POD_NAME", "unknown")

    def get_last_delivered_id(self, stream: str) -> str:
        groups = self.client.xinfo_groups(stream)
        for group in groups:
            if group["name"] == self.streams[stream]:
                return group["last-delivered-id"]

    def group_consume(
        self,
        streams: list[str] = None,
        group: str = None,
        count: int = 1,
    ) -> list[queue_messages.Message]:
        message = []
        streams = (
            {stream: self.streams.get(stream, self.get_name()) for stream in streams}
            if streams is not None
            else self.streams
        )

        for stream, default_group in streams.items():
            last_delivered_id = ">"
            all_messages = self.client.xreadgroup(
                groupname=group if group is not None else default_group,
                consumername=self.name,
                streams={stream: last_delivered_id},
                count=count,
            )
            for stream_message in all_messages:
                stream = stream_message[0]
                records = stream_message[1]
                for record in records:
                    record_id = record[0]
                    payload = record[1]
                    body = json.loads(payload.get("body", "{}"))
                    message.append(
                        queue_messages.Message(
                            header=queue_messages.Header(
                                id=record_id,
                                stream=stream,
                                group=group,
                                consumer=self.name,
                            ),
                            body=body,
                        )
                    )
        return message

    def delete_from_stream(self, stream: str, *record_id: str):
        return self.client.xdel(stream, *record_id)

    def _clear_stream(self, stream: str):
        return self.client.xtrim(stream, maxlen=0)

    def _clear_all_streams(self):
        for stream in self.streams:
            self._clear_stream(stream)

    # def create_config(self) -> RedisConfig:
    #     config = RedisConfig(**self.config)

    def __init_consumer_streams(self) -> dict[str, str]:
        streams = self.config.consumer.streams
        for stream in streams:
            if streams[stream] is None:
                streams[stream] = self.default_group
        return streams

    def __init_consumer_group(self):
        for stream, group in self.streams.items():
            try:
                self.client.xgroup_create(stream, group, mkstream=True)
            except redis.ResponseError as e:
                if "BUSYGROUP Consumer Group name already exists" not in str(e):
                    raise
                continue

    def publish_event(self, event: core.Event, **kwargs) -> Any:
        message: dict[str, str] = self.create_message_from_event(event)
        stream = self.get_event_stream(event)
        response = self.client.xadd(name=stream, fields=message, **kwargs)
        return response

    def create_message_from_event(self, event: core.Event) -> dict[str, str]:
        body = event.model_dump_json()
        return {"body": body}

    def create_client(self, *args, **kwargs) -> redis.Redis:
        redis_config: dict[str, Any] = (
            self.config.connection.model_dump() | self.config.args
        )
        return redis.Redis(**redis_config)
