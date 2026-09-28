import json
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Iterable

from src.domain.telemetry_event import TelemetryEvent


class EventRepository:
    def __init__(
        self,
        db_path: str | Path = "greenmove_events.db",
    ) -> None:
        self.db_path = str(db_path)
        self._initialize()

    @contextmanager
    def _connection(
        self,
    ) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(
            self.db_path
        )
        connection.row_factory = sqlite3.Row

        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    synced INTEGER NOT NULL DEFAULT 0
                )
                """
            )

    def add(
        self,
        event: TelemetryEvent,
    ) -> int:
        with self._connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO events(
                    event_type,
                    payload,
                    created_at,
                    synced
                )
                VALUES (?, ?, ?, 0)
                """,
                (
                    event.event_type,
                    json.dumps(event.payload),
                    event.created_at,
                ),
            )

            return int(cursor.lastrowid)

    def pending(
        self,
        limit: int = 100,
    ) -> list[dict]:
        with self._connection() as connection:
            rows = connection.execute(
                """
                SELECT
                    id,
                    event_type,
                    payload,
                    created_at
                FROM events
                WHERE synced = 0
                ORDER BY id
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        return [
            {
                "id": int(row["id"]),
                "event_type": row["event_type"],
                "payload": json.loads(
                    row["payload"]
                ),
                "created_at": row["created_at"],
            }
            for row in rows
        ]

    def mark_synced(
        self,
        event_ids: Iterable[int],
    ) -> None:
        ids = list(event_ids)

        if not ids:
            return

        placeholders = ",".join(
            "?" for _ in ids
        )

        with self._connection() as connection:
            connection.execute(
                f"""
                UPDATE events
                SET synced = 1
                WHERE id IN ({placeholders})
                """,
                ids,
            )

    def pending_count(self) -> int:
        with self._connection() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM events
                WHERE synced = 0
                """
            ).fetchone()

        return int(row["count"])