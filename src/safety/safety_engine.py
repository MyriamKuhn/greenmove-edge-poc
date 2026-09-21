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