# DCS Theater Engine

External dynamic campaign engine for Digital Combat Simulator.

The campaign engine owns the persistent war state and generates focused DCS
missions from that state. DCS is treated as a high-fidelity mission renderer:
the player flies a tailored mission, results are imported afterward, and the
campaign continues outside DCS.

## Development

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
```

Run the local UI:

```bash
.venv/bin/python -m uvicorn "dcs_theater_engine.api.app:create_app" --factory --reload
```

Then open `http://127.0.0.1:8000`.

The map UI uses Leaflet with OpenStreetMap tiles as the base map, so the browser
needs internet access for the map background to load.
