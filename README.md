# GreenMove Edge POC

Proof of concept for GreenMove Logistics demonstrating offline ZFE geofencing and telematics-based harsh braking detection on constrained edge hardware.

The project contains two independent modules:

- **Geo Engine**: detects whether simulated GPS positions enter the Lyon ZFE using a Bounding Box optimization followed by a Ray Casting Point-in-Polygon algorithm.
- **Safety Engine**: analyzes longitudinal accelerometer data and detects harsh braking events using a lightweight threshold-based filter.

The POC is designed to run locally without any network dependency.

## Requirements

- Python 3.10 or later
- pip
- Git

The project was developed and tested with:

- Python 3.14.4
- pytest 9.1.1

No external library is required by the application itself. `pytest` is only used for automated tests.

## Installation

Clone the repository:

```bash
git clone https://github.com/MyriamKuhn/greenmove-edge-poc.git
cd greenmove-edge-poc
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows with Git Bash:

```bash
source .venv/Scripts/activate
```

On Windows Command Prompt:

```cmd
.venv\Scripts\activate
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

Install the test dependency:

```bash
python -m pip install -r requirements.txt
```

## Project Structure

```text
greenmove-edge-poc/
├── data/
│   ├── accelerometer_data.csv
│   ├── lyon_polygon.json
│   └── truck_gps.json
├── src/
│   ├── geo/
│   │   ├── geo_engine.py
│   │   └── run_geo.py
│   └── safety/
│       ├── safety_engine.py
│       └── run_safety.py
├── tests/
│   ├── geo/
│   │   └── test_geo_engine.py
│   └── safety/
│       └── test_safety_engine.py
├── .gitignore
├── requirements.txt
└── README.md
```

## Run the Geo Engine

From the project root:

```bash
python -m src.geo.run_geo
```

Example output:

```text
[GPS OUT] id=1 time=08:00:00
[GPS OUT] id=2 time=08:00:10
[GPS OUT] id=3 time=08:00:20
[ALERT ZFE] id=4 time=08:00:30 lat=45.76 lon=4.8357
[ALERT ZFE] id=5 time=08:00:40 lat=45.75 lon=4.85
```

The Geo Engine works entirely from locally stored JSON files and does not require a network connection.

## Run the Safety Engine

From the project root:

```bash
python -m src.safety.run_safety
```

Example output:

```text
[HARSH BRAKING] timestamp=1678880005 acc_y=-3.45 m/s²
[SAFETY SUMMARY] samples=10 harsh_braking_events=1
[OUTPUT] daily_score.json
```

The command generates a `daily_score.json` file in the project root.

Example:

```json
{
  "total_samples": 10,
  "harsh_braking_events": 1,
  "events": [
    {
      "timestamp": 1678880005,
      "acc_y": -3.45
    }
  ]
}
```

## Run the Tests

Run all automated tests with:

```bash
python -m pytest -v
```

The current test suite contains 17 tests covering both the Geo and Safety engines.

## Input Files

The POC uses three local input files stored in the `data/` directory.

### `lyon_polygon.json`

Defines the simplified Lyon ZFE polygon as latitude/longitude coordinates.

The first and last coordinates are identical in order to explicitly close the polygon.

### `truck_gps.json`

Contains a simulated truck GPS trace.

Each entry includes:

- an identifier;
- a timestamp;
- latitude;
- longitude;
- an `expected` field supplied by the exercise dataset.

The Geo Engine uses the coordinates themselves for the geometric calculation.

### `accelerometer_data.csv`

Contains accelerometer samples with the following columns:

```text
timestamp,acc_x,acc_y,acc_z
```

The longitudinal axis used for braking detection is `acc_y`.

A strong negative Y acceleration represents vehicle deceleration.

## Geo Algorithm

### Bounding Box Optimization

Before executing the Point-in-Polygon calculation, the Geo Engine computes the polygon bounding box:

```text
min_lat
max_lat
min_lon
max_lon
```

For each GPS position, the engine first checks whether the point is inside this rectangle.

If the point is outside the bounding box, it cannot be inside the ZFE polygon and is immediately rejected.

This avoids running the more detailed Ray Casting calculation for obviously distant points.

### Ray Casting / Point in Polygon

For points that pass the Bounding Box check, the engine uses the Ray Casting algorithm.

Conceptually, a horizontal ray is projected from the GPS point toward one side of the plane.

The algorithm counts how many polygon edges intersect this ray:

- an odd number of intersections means the point is inside the polygon;
- an even number of intersections means the point is outside the polygon.

The implementation also explicitly checks whether a point lies directly on a polygon segment. Boundary points are considered inside the ZFE.

The algorithm processes each polygon edge once, resulting in linear complexity relative to the number of polygon vertices:

```text
O(N)
```

This is appropriate for the constrained edge hardware targeted by the POC.

## Safety Algorithm

The Safety Engine reads accelerometer samples sequentially and focuses on the longitudinal Y axis.

The exercise dataset is expressed in `m/s²`.

A harsh braking event is detected when:

```text
acc_y < -2.5
```

For example:

```text
-0.80 m/s²  -> normal variation
-1.20 m/s²  -> normal variation
-3.45 m/s²  -> harsh braking
```

The threshold therefore acts as a lightweight filtering mechanism: small variations and vehicle vibrations are ignored, while significant longitudinal deceleration is retained as an event.

A moving average was intentionally not used for this POC because smoothing a very short event could reduce its amplitude and hide the braking peak.

The Safety Engine processes each sample once:

```text
O(N)
```

This keeps CPU and memory usage low.

## Output Files

### Geo Output

The Geo Engine writes its results to standard output.

When a GPS point is detected inside the ZFE, the following log format is produced:

```text
[ALERT ZFE] id=4 time=08:00:30 lat=45.76 lon=4.8357
```

Positions outside the zone are logged as:

```text
[GPS OUT] id=1 time=08:00:00
```

### Safety Output

The Safety Engine generates:

```text
daily_score.json
```

The generated file contains:

- the number of processed accelerometer samples;
- the number of detected harsh braking events;
- the timestamp and longitudinal acceleration of each event.

The output file is generated at runtime and is therefore excluded from Git through `.gitignore`.

## Error Handling

The POC handles common input errors without displaying an uncontrolled traceback during normal execution.

Handled cases include:

- missing JSON input files;
- invalid JSON syntax;
- missing CSV input files;
- invalid numeric values in accelerometer data;
- missing or malformed required fields.

Example:

```text
[ERROR] File not found: data/truck_gps.json
```

or:

```text
[ERROR] File not found: data/accelerometer_data.csv
```

This behavior is particularly important for the live demonstration because invalid input should be reported clearly without crashing the complete application flow.

## Dataset Note

The GPS dataset supplied with the exercise contains the following entry:

```json
{
  "id": 3,
  "timestamp": "08:00:20",
  "lat": 45.7850,
  "lon": 4.8050,
  "expected": "IN (Bordure)"
}
```

Using the polygon coordinates supplied in the same dataset, this point is geometrically outside the polygon according to the implemented Ray Casting calculation.

The implementation intentionally does not alter the algorithm to force the value of the `expected` field.

A separate automated test verifies that a point located exactly on a polygon boundary is correctly considered inside.

This keeps the geometric implementation deterministic while documenting the dataset inconsistency explicitly.

## Performance Considerations

The target Zebra ET40 environment has limited application memory and may receive up to 100 sensor points per second.

The POC therefore follows several lightweight design principles:

- no external geospatial framework;
- no pandas or NumPy dependency;
- sequential processing of GPS and accelerometer samples;
- Bounding Box rejection before Ray Casting;
- O(N) processing instead of nested O(N²) algorithms;
- local processing without network dependency;
- compact JSON output containing detected events instead of raw sensor history.

The Bounding Box is calculated once and reused for all GPS points.

For the Safety module, samples are read and processed with Python's standard CSV library.

## Limitations of the POC

This project is intentionally limited to the technical feasibility requested by the proof of concept.

Current limitations include:

- the ZFE polygon is a simplified static dataset;
- there is no production-grade European map database;
- there is no Android sensor integration;
- GPS data is simulated from a JSON file;
- accelerometer data is simulated from a CSV file;
- the harsh braking threshold is fixed;
- the daily report does not implement an insurer-specific scoring formula;
- there is no local database or deferred Cloud synchronization yet;
- there is no graphical driver interface.

These elements would belong to a production implementation rather than to the core feasibility POC.

## Design Rationale

The implementation deliberately favors simple and deterministic algorithms.

The Geo module validates that ZFE detection can operate without network access, directly addressing the failure mode of the previous Cloud-dependent application.

The Safety module validates that local accelerometer data can produce behavioral driving evidence by isolating significant braking events from normal variations.

Both modules use only lightweight processing and local files, making the POC suitable for demonstrating the Edge Computing approach on constrained hardware.