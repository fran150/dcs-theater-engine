"""Marianas theater map data.

Positions are stored in DCS world coordinates, in meters. Airport data comes
from pydcs so DCS-owned terrain details stay aligned with the simulator data.
"""

from __future__ import annotations

from typing import Any

from dcs.terrain.marianaislands import MarianaIslands
from dcs.terrain.marianaislands.projection import PARAMETERS as MARIANAS_PARAMETERS

from dcs_theater_engine.data.coordinates import DcsPoint
from dcs_theater_engine.data.definitions import AirbaseDefinition, TheaterDefinition
from dcs_theater_engine.data.pydcs_adapter import (
    airbases_from_pydcs,
    projection_from_pydcs,
)

MapPolygon = tuple[DcsPoint, ...]

MARIANAS_PROJECTION = projection_from_pydcs(MARIANAS_PARAMETERS)


def dcs_polygon(points: tuple[tuple[float, float], ...]) -> MapPolygon:
    """Create a polygon from DCS map coordinates."""

    return tuple(DcsPoint(x=x, y=y) for x, y in points)


def marianas_airbases_from_pydcs() -> tuple[dict[str, Any], ...]:
    """Load Marianas airports from pydcs."""

    return airbases_from_pydcs(MarianaIslands())


MARIANAS_AIRBASES: tuple[dict[str, Any], ...] = marianas_airbases_from_pydcs()

MARIANAS_LAND_POLYGONS: dict[str, MapPolygon] = {
    "Guam": dcs_polygon(
        (
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
        )
    ),
    "Rota": dcs_polygon(
        (
            (70800, 42800),
            (74400, 39200),
            (78700, 40300),
            (82400, 46200),
            (80700, 52200),
            (75500, 54000),
            (71500, 50100),
        )
    ),
    "Tinian": dcs_polygon(
        (
            (158400, 85100),
            (163500, 81700),
            (170700, 85400),
            (174100, 93800),
            (169800, 99800),
            (162700, 95700),
        )
    ),
    "Saipan": dcs_polygon(
        (
            (171500, 95000),
            (177600, 90700),
            (186700, 98500),
            (188900, 111400),
            (182800, 119700),
            (174300, 112700),
        )
    ),
    "Pagan": dcs_polygon(
        (
            (503800, 103000),
            (511800, 99000),
            (521200, 104200),
            (522700, 113500),
            (513800, 118300),
            (505100, 112900),
        )
    ),
}

MARIANAS_MAP_BOUNDS = {
    "xMin": -300000,
    "xMax": 1000000,
    "yMin": -1000000,
    "yMax": 500000,
}

MARIANAS_THEATER = TheaterDefinition(
    id="marianas",
    name="Mariana Islands",
    airbases=tuple(
        AirbaseDefinition(
            id=airbase["id"],
            name=airbase["name"],
            position=airbase["point"],
            dcs_airport_id=airbase["dcs_airport_id"],
        )
        for airbase in MARIANAS_AIRBASES
    ),
    land_polygons=tuple(MARIANAS_LAND_POLYGONS.values()),
)


def point_payload(point: DcsPoint) -> dict[str, float]:
    """Return a JSON-friendly DCS point."""

    return {"x": point.x, "y": point.y}


def lat_lon_payload(point: DcsPoint) -> dict[str, float]:
    """Return a JSON-friendly WGS84 point for map clients."""

    lat_lon = MARIANAS_PROJECTION.to_lat_lon(point)
    return {"latitude": lat_lon.latitude, "longitude": lat_lon.longitude}


def airbase_payload(airbase: dict[str, Any]) -> dict[str, Any]:
    """Return API airbase data with derived map coordinates."""

    point = airbase["point"]
    payload = {key: value for key, value in airbase.items() if key != "point"}
    payload["point"] = point_payload(point)
    payload.update(lat_lon_payload(point))
    return payload


def bounds_payload() -> dict[str, Any]:
    """Return DCS bounds and a WGS84 outline for Leaflet fitting."""

    bounds = dict(MARIANAS_MAP_BOUNDS)
    x_min = bounds["xMin"]
    x_max = bounds["xMax"]
    y_min = bounds["yMin"]
    y_max = bounds["yMax"]
    samples = 12

    points: list[DcsPoint] = []
    for index in range(samples + 1):
        x = x_min + (x_max - x_min) * index / samples
        points.append(DcsPoint(x=x, y=y_min))
    for index in range(1, samples + 1):
        y = y_min + (y_max - y_min) * index / samples
        points.append(DcsPoint(x=x_max, y=y))
    for index in range(1, samples + 1):
        x = x_max - (x_max - x_min) * index / samples
        points.append(DcsPoint(x=x, y=y_max))
    for index in range(1, samples):
        y = y_max - (y_max - y_min) * index / samples
        points.append(DcsPoint(x=x_min, y=y))

    bounds["outline"] = [lat_lon_payload(point) for point in points]
    return bounds


def marianas_map_payload() -> dict[str, Any]:
    """Return the first UI map payload for the Marianas theater."""

    return {
        "id": MARIANAS_THEATER.id,
        "name": MARIANAS_THEATER.name,
        "source": "pydcs MarianaIslands terrain",
        "projection": "DCS world coordinates in meters, projected to WGS84 for UI",
        "bounds": bounds_payload(),
        "islands": [
            {"name": name, "points": [point_payload(point) for point in points]}
            for name, points in MARIANAS_LAND_POLYGONS.items()
        ],
        "airbases": [airbase_payload(airbase) for airbase in MARIANAS_AIRBASES],
    }
