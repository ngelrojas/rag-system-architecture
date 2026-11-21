# relay.py — polls the outbox and publishes; runs as its own small process (3.8)
#
#   uv run python relay.py        (needs DATABASE_URL, e.g. from docker compose)
#
# Decoupled from the request path entirely: if the broker is down, events
# wait in the outbox instead of being lost.
import json
import logging
import os
import time
from typing import Any, Protocol

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("relay")


class MessageQueue(Protocol):
    def publish(self, topic: str, payload: str) -> None: ...


class LoggingMessageQueue:
    """Stand-in broker: logs each event. Swap for Kafka, SQS, RabbitMQ..."""

    def publish(self, topic: str, payload: str) -> None:
        log.info("published %s %s", topic, payload)


def relay_once(db_connection: Any, message_queue: MessageQueue, batch_size: int = 100) -> int:
    unpublished = db_connection.execute(
        "SELECT id, event_type, payload FROM outbox WHERE published = false "
        "ORDER BY created_at LIMIT %s",
        (batch_size,),
    ).fetchall()
    for row in unpublished:
        payload = row.payload if isinstance(row.payload, str) else json.dumps(row.payload)
        message_queue.publish(topic=row.event_type, payload=payload)
        db_connection.execute("UPDATE outbox SET published = true WHERE id = %s", (row.id,))
    return len(unpublished)


def relay_outbox_events(db_connection: Any, message_queue: MessageQueue, poll_interval_s: float = 1.0) -> None:
    while True:
        relay_once(db_connection, message_queue)
        time.sleep(poll_interval_s)


if __name__ == "__main__":
    import psycopg
    from psycopg.rows import namedtuple_row

    url = os.environ.get("DATABASE_URL", "postgresql://rag:rag@localhost:5432/rag")
    with psycopg.connect(url, autocommit=True, row_factory=namedtuple_row) as conn:
        relay_outbox_events(conn, LoggingMessageQueue())
