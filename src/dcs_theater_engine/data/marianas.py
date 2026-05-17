"""Marianas theater map data.

The airfield positions are taken from the pydcs MarianaIslands terrain data and
stored here as a small snapshot so the UI can start without importing pydcs on
non-Windows development machines.
"""

from __future__ import annotations

from typing import Any

from dcs_theater_engine.data.definitions import AirbaseDefinition, TheaterDefinition

MapPoint = tuple[float, float]
MapPolygon = tuple[MapPoint, ...]

MARIANAS_AIRBASES: tuple[dict[str, Any], ...] = (
    {
        "id": "rota-intl",
        "name": "Rota Intl",
        "category": "civilian",
        "point": {"x": 75884.859375, "y": 48589.876953},
        "latitude": 14.17437267,
        "longitude": 145.24109240,
        "runways": [{"name": "9-27", "heading": 90}],
        "parking_slots": 9,
    },
    {
        "id": "saipan-intl",
        "name": "Saipan Intl",
        "category": "civilian",
        "point": {"x": 180035.4375, "y": 101855.960938},
        "latitude": 15.11893105,
        "longitude": 145.72912914,
        "runways": [{"name": "07-25", "heading": 70}],
        "parking_slots": 19,
    },
    {
        "id": "tinian-intl",
        "name": "Tinian Intl",
        "category": "civilian",
        "point": {"x": 166859.859375, "y": 89956.625},
        "latitude": 14.99919363,
        "longitude": 145.61918162,
        "runways": [{"name": "08-26", "heading": 80}],
        "parking_slots": 4,
    },
    {
        "id": "antonio-b-won-pat-intl",
        "name": "Antonio B. Won Pat Intl",
        "category": "civilian",
        "point": {"x": -23.656158, "y": -77.940308},
        "latitude": 13.48477976,
        "longitude": 144.79682382,
        "runways": [
            {"name": "06R-24L", "heading": 60},
            {"name": "06L-24R", "heading": 60},
        ],
        "parking_slots": 23,
    },
    {
        "id": "olf-orote",
        "name": "Olf Orote",
        "category": "military",
        "point": {"x": -5023.305023, "y": -16869.435119},
        "latitude": 13.43820057,
        "longitude": 144.64223968,
        "runways": [{"name": "25-7", "heading": 250}],
        "parking_slots": 4,
    },
    {
        "id": "andersen-afb",
        "name": "Andersen AFB",
        "category": "military",
        "point": {"x": 10574.989746, "y": 14548.833496},
        "latitude": 13.58170286,
        "longitude": 144.93105130,
        "runways": [
            {"name": "06L-24R", "heading": 60},
            {"name": "06R-24L", "heading": 60},
        ],
        "parking_slots": 194,
    },
    {
        "id": "pagan-airstrip",
        "name": "Pagan Airstrip",
        "category": "military",
        "point": {"x": 512410.262497, "y": 107564.608564},
        "latitude": 18.12315374,
        "longitude": 145.76314859,
        "runways": [{"name": "11-29", "heading": 110}],
        "parking_slots": 3,
    },
    {
        "id": "north-west-field",
        "name": "North West Field",
        "category": "military",
        "point": {"x": 15909.476563, "y": 7619.561523},
        "latitude": 13.62936579,
        "longitude": 144.86661165,
        "runways": [],
        "parking_slots": 8,
    },
)

MARIANAS_LAND_POLYGONS: dict[str, MapPolygon] = {
    "Guam": (
        (-13200, -24100),
        (-5700, -28900),
        (2600, -25400),
        (9200, -15100),
        (16700, -4200),
        (24700, 9300),
        (23800, 20300),
        (15900, 25800),
        (6100, 22200),
        (-2600, 10800),
        (-10800, -5100),
    ),
    "Rota": (
        (70800, 42800),
        (74400, 39200),
        (78700, 40300),
        (82400, 46200),
        (80700, 52200),
        (75500, 54000),
        (71500, 50100),
    ),
    "Tinian": (
        (158400, 85100),
        (163500, 81700),
        (170700, 85400),
        (174100, 93800),
        (169800, 99800),
        (162700, 95700),
    ),
    "Saipan": (
        (171500, 95000),
        (177600, 90700),
        (186700, 98500),
        (188900, 111400),
        (182800, 119700),
        (174300, 112700),
    ),
    "Pagan": (
        (503800, 103000),
        (511800, 99000),
        (521200, 104200),
        (522700, 113500),
        (513800, 118300),
        (505100, 112900),
    ),
}

MARIANAS_MAP_BOUNDS = {
    "xMin": -30000,
    "xMax": 535000,
    "yMin": -35000,
    "yMax": 135000,
}

MARIANAS_THEATER = TheaterDefinition(
    id="marianas",
    name="Mariana Islands",
    airbases=tuple(
        AirbaseDefinition(
            id=airbase["id"],
            name=airbase["name"],
            latitude=airbase["latitude"],
            longitude=airbase["longitude"],
        )
        for airbase in MARIANAS_AIRBASES
    ),
    land_polygons=tuple(MARIANAS_LAND_POLYGONS.values()),
)


def marianas_map_payload() -> dict[str, Any]:
    """Return the first UI map payload for the Marianas theater."""

    return {
        "id": MARIANAS_THEATER.id,
        "name": MARIANAS_THEATER.name,
        "source": "pydcs MarianaIslands terrain snapshot",
        "projection": "DCS world coordinates, meters",
        "bounds": MARIANAS_MAP_BOUNDS,
        "islands": [
            {"name": name, "points": points}
            for name, points in MARIANAS_LAND_POLYGONS.items()
        ],
        "airbases": MARIANAS_AIRBASES,
    }
