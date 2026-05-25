"""Marianas theater map data.

Positions are stored in DCS world coordinates, in meters. Airport data comes
from pydcs so DCS-owned terrain details stay aligned with the simulator data.
"""

from __future__ import annotations

from typing import Any

from dcs import ships as dcs_ships
from dcs.terrain.marianaislands import MarianaIslands
from dcs.terrain.marianaislands.projection import PARAMETERS as MARIANAS_PARAMETERS

from dcs_theater_engine.data.coordinates import DcsPoint
from dcs_theater_engine.data.definitions import (
    AirbaseDefinition,
    CarrierGroupDefinition,
    ShipDefinition,
    ShipTypeDefinition,
    TheaterDefinition,
)
from dcs_theater_engine.data.pydcs_adapter import (
    airbases_from_pydcs,
    projection_from_pydcs,
    ship_type_from_pydcs,
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

STENNIS_SHIP_TYPE = ship_type_from_pydcs(dcs_ships.Stennis)
TICONDEROGA_SHIP_TYPE = ship_type_from_pydcs(dcs_ships.TICONDEROG)
ARLEIGH_BURKE_SHIP_TYPE = ship_type_from_pydcs(dcs_ships.USS_Arleigh_Burke_IIa)
KUZNETSOV_SHIP_TYPE = ship_type_from_pydcs(dcs_ships.KUZNECOW)
PYOTR_VELIKIY_SHIP_TYPE = ship_type_from_pydcs(dcs_ships.PIOTR)
NEUSTRASHIMY_SHIP_TYPE = ship_type_from_pydcs(dcs_ships.NEUSTRASH)

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

MARIANAS_CARRIER_GROUPS: tuple[CarrierGroupDefinition, ...] = (
    CarrierGroupDefinition(
        id="us-carrier-group-southeast",
        name="US Carrier Group Southeast",
        country="USA",
        coalition="blue",
        position=DcsPoint(x=-160000, y=260000),
        heading=315.0,
        ships=(
            ShipDefinition(
                id="uss-john-c-stennis",
                name="USS John C. Stennis",
                ship_type=STENNIS_SHIP_TYPE,
                position=DcsPoint(x=-160000, y=260000),
                heading=315.0,
            ),
            ShipDefinition(
                id="uss-ticonderoga-screen",
                name="USS Ticonderoga Screen",
                ship_type=TICONDEROGA_SHIP_TYPE,
                position=DcsPoint(x=-156000, y=255000),
                heading=315.0,
            ),
            ShipDefinition(
                id="uss-arleigh-burke-screen",
                name="USS Arleigh Burke Screen",
                ship_type=ARLEIGH_BURKE_SHIP_TYPE,
                position=DcsPoint(x=-164000, y=255000),
                heading=315.0,
            ),
        ),
    ),
    CarrierGroupDefinition(
        id="russian-carrier-group-northwest",
        name="Russian Carrier Group Northwest",
        country="Russia",
        coalition="red",
        position=DcsPoint(x=650000, y=-180000),
        heading=135.0,
        ships=(
            ShipDefinition(
                id="admiral-kuznetsov",
                name="Admiral Kuznetsov",
                ship_type=KUZNETSOV_SHIP_TYPE,
                position=DcsPoint(x=650000, y=-180000),
                heading=135.0,
            ),
            ShipDefinition(
                id="pyotr-velikiy-screen",
                name="Pyotr Velikiy Screen",
                ship_type=PYOTR_VELIKIY_SHIP_TYPE,
                position=DcsPoint(x=654000, y=-185000),
                heading=135.0,
            ),
            ShipDefinition(
                id="neustrashimy-screen",
                name="Neustrashimy Screen",
                ship_type=NEUSTRASHIMY_SHIP_TYPE,
                position=DcsPoint(x=646000, y=-185000),
                heading=135.0,
            ),
        ),
    ),
)

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
    carrier_groups=MARIANAS_CARRIER_GROUPS,
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


def ship_type_payload(ship_type: ShipTypeDefinition) -> dict[str, Any]:
    """Return API ship type metadata."""

    return {
        "id": ship_type.id,
        "display_name": ship_type.display_name,
        "dcs_type_name": ship_type.dcs_type_name,
        "plane_capacity": ship_type.plane_capacity,
        "helicopter_capacity": ship_type.helicopter_capacity,
        "parking_slots": ship_type.parking_slots,
        "detection_range_m": ship_type.detection_range_m,
        "threat_range_m": ship_type.threat_range_m,
        "air_weapon_distance_m": ship_type.air_weapon_distance_m,
    }


def ship_payload(ship: ShipDefinition) -> dict[str, Any]:
    """Return API ship placement data with pydcs type metadata."""

    return {
        "id": ship.id,
        "name": ship.name,
        "ship_type": ship_type_payload(ship.ship_type),
        "point": point_payload(ship.position),
        "heading": ship.heading,
        **lat_lon_payload(ship.position),
    }


def carrier_group_payload(group: CarrierGroupDefinition) -> dict[str, Any]:
    """Return API carrier group data with derived map coordinates."""

    return {
        "id": group.id,
        "name": group.name,
        "country": group.country,
        "coalition": group.coalition,
        "point": point_payload(group.position),
        "heading": group.heading,
        "ships": [ship_payload(ship) for ship in group.ships],
        **lat_lon_payload(group.position),
    }


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
        "carrier_groups": [
            carrier_group_payload(group) for group in MARIANAS_THEATER.carrier_groups
        ],
    }
