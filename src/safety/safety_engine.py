import json
import csv
from pathlib import Path


HARSH_BRAKING_THRESHOLD = -2.5


def load_accelerometer_data(file_path: str) -> list[dict]:
    """Load accelerometer samples from a CSV file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    samples = []

    with path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            samples.append(
                {
                    "timestamp": int(row["timestamp"]),
                    "acc_x": float(row["acc_x"]),
                    "acc_y": float(row["acc_y"]),
                    "acc_z": float(row["acc_z"]),
                }
            )

    return samples


def is_harsh_braking(acc_y: float) -> bool:
    """Return True when longitudinal deceleration exceeds the threshold."""
    return acc_y < HARSH_BRAKING_THRESHOLD


def detect_harsh_braking_events(samples: list[dict]) -> list[dict]:
    """Return samples identified as harsh braking events."""
    events = []

    for sample in samples:
        if is_harsh_braking(sample["acc_y"]):
            events.append(sample)

    return events

def build_daily_score(samples: list[dict], events: list[dict]) -> dict:
    """Build a daily safety summary from accelerometer samples."""
    return {
        "total_samples": len(samples),
        "harsh_braking_events": len(events),
        "events": [
            {
                "timestamp": event["timestamp"],
                "acc_y": event["acc_y"],
            }
            for event in events
        ],
    }


def write_daily_score(score: dict, output_path: str) -> None:
    """Write the daily safety summary to a JSON file."""
    path = Path(output_path)

    with path.open("w", encoding="utf-8") as file:
        json.dump(score, file, indent=2)