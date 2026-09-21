import json
from pathlib import Path


def load_json_file(file_path: str) -> list[dict]:
    """Load and return JSON data from a file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def calculate_bounding_box(polygon: list[dict]) -> dict:
    """Calculate the minimum bounding box around a polygon."""
    latitudes = [point["lat"] for point in polygon]
    longitudes = [point["lon"] for point in polygon]

    return {
        "min_lat": min(latitudes),
        "max_lat": max(latitudes),
        "min_lon": min(longitudes),
        "max_lon": max(longitudes),
    }


def is_inside_bounding_box(point: dict, bbox: dict) -> bool:
    """Return True if a point is inside or on the bounding box."""
    return (
        bbox["min_lat"] <= point["lat"] <= bbox["max_lat"]
        and bbox["min_lon"] <= point["lon"] <= bbox["max_lon"]
    )