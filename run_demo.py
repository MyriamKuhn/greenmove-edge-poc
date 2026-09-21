from src.geo.run_geo import run_geo_engine
from src.safety.run_safety import run_safety_engine


def run_demo() -> None:
    """Run the complete GreenMove Edge POC demonstration."""
    print("=== GREENMOVE EDGE POC ===")
    print()

    print("=== GEO ENGINE ===")
    run_geo_engine()

    print()
    print("=== SAFETY ENGINE ===")
    run_safety_engine()

    print()
    print("=== DEMO COMPLETE ===")


if __name__ == "__main__":
    run_demo()