from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class TelemetryEvent:
    event_type: str
    payload: dict[str, Any]
    created_at: str

    @classmethod
    def harsh_braking(
        cls,
        acc_y: float,
        timestamp: int | float,
    ) -> "TelemetryEvent":
        return cls(
            event_type="harsh_braking",
            payload={
                "timestamp": timestamp,
                "acc_y": acc_y,
            },
            created_at=datetime.now(timezone.utc).isoformat(),
        )