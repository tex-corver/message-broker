from . import redis_adapter

adapter_routers = {
    "redis": redis_adapter.ComponentFactory,
}
