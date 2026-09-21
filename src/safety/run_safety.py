import csv

from src.safety.safety_engine import (
    build_daily_score,
    detect_harsh_braking_events,
    load_accelerometer_data,
    write_daily_score,
)


INPUT_FILE = "data/accelerometer_data.csv"
OUTPUT_FILE = "daily_score.json"


def run_safety_engine() -> None:
    """Run harsh braking detection and generate the daily safety report."""
    try:
        samples = load_accelerometer_data(INPUT_FILE)
        events = detect_harsh_braking_events(samples)
        score = build_daily_score(samples, events)

        for event in events:
            print(
                f'[HARSH BRAKING] timestamp={event["timestamp"]} '
                f'acc_y={event["acc_y"]} m/s²'
            )

        write_daily_score(score, OUTPUT_FILE)

        print(
            f"[SAFETY SUMMARY] samples={len(samples)} "
            f"harsh_braking_events={len(events)}"
        )
        print(f"[OUTPUT] {OUTPUT_FILE}")

    except FileNotFoundError as error:
        print(f"[ERROR] {error}")
    except (csv.Error, KeyError, TypeError, ValueError) as error:
        print(f"[ERROR] Invalid Safety input data: {error}")


if __name__ == "__main__":
    run_safety_engine()