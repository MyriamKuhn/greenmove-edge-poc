from collections.abc import Callable
from typing import Any

from src.storage.event_repository import EventRepository


Sender = Callable[
    [dict[str, Any], float],
    None,
]


class SyncService:
    def __init__(
        self,
        repository: EventRepository,
        sender: Sender,
        timeout_seconds: float = 2.0,
        max_attempts: int = 3,
    ) -> None:
        self.repository = repository
        self.sender = sender
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    def sync_pending(
        self,
        limit: int = 100,
    ) -> dict[str, int]:
        synced_ids: list[int] = []
        failed = 0

        for event in self.repository.pending(limit):
            delivered = False

            for _ in range(self.max_attempts):
                try:
                    self.sender(
                        event,
                        self.timeout_seconds,
                    )
                    delivered = True
                    break

                except (
                    ConnectionError,
                    TimeoutError,
                    OSError,
                ):
                    continue

            if delivered:
                synced_ids.append(event["id"])
            else:
                failed += 1

        self.repository.mark_synced(
            synced_ids
        )

        return {
            "synced": len(synced_ids),
            "failed": failed,
        }