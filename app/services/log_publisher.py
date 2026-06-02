import json
import logging
from datetime import datetime, timezone
from typing import Any, Literal, Optional

import aio_pika

from app.config import settings

logger = logging.getLogger("fakeradar.logs")

_connection: aio_pika.RobustConnection | None = None
_channel: aio_pika.abc.AbstractChannel | None = None

LogLevel = Literal["info", "warn", "error"]


async def init_log_publisher() -> None:
    global _connection, _channel
    if not settings.rabbitmq_url:
        logger.info("Log publisher disabled: RABBITMQ_URL not set")
        return
    try:
        _connection = await aio_pika.connect_robust(settings.rabbitmq_url)
        _channel = await _connection.channel()
        await _channel.declare_queue(settings.log_queue, durable=True)
        await publish_log(
            service="ai",
            level="info",
            event="service.started",
            message="AI log publisher connected",
        )
        logger.info("Log publisher connected (queue=%s)", settings.log_queue)
    except Exception as e:
        logger.warning("Log publisher: could not connect to RabbitMQ: %s", e)


async def publish_log(
    *,
    service: str = "ai",
    level: LogLevel = "info",
    event: str,
    message: str,
    metadata: Optional[dict[str, Any]] = None,
) -> None:
    if not _channel:
        return
    payload = {
        "service": service,
        "level": level,
        "event": event,
        "message": message,
        "metadata": metadata or {},
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await _channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(payload).encode("utf-8"),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=settings.log_queue,
        )
    except Exception as e:
        logger.warning("Log publisher: failed to send message: %s", e)


async def close_log_publisher() -> None:
    global _connection, _channel
    if _connection:
        await _connection.close()
    _connection = None
    _channel = None
