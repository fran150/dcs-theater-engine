"""Adapters for reading static theater data from pydcs."""

from __future__ import annotations

import re
from typing import Any

from dcs_theater_engine.data.coordinates import DcsPoint, TransverseMercatorProjection
from dcs_theater_engine.data.definitions import ShipTypeDefinition

PYDCS_ID_PATTERN = re.compile(r"[^a-z0-9]+")


def projection_from_pydcs(parameters: Any) -> TransverseMercatorProjection:
    """Create the local projection helper from pydcs terrain parameters."""

    return TransverseMercatorProjection(
        central_meridian=parameters.central_meridian,
        false_easting=parameters.false_easting,
        false_northing=parameters.false_northing,
        scale_factor=parameters.scale_factor,
    )


def airbase_id(name: str) -> str:
    """Create a campaign-friendly ID from a pydcs airport name."""

    return PYDCS_ID_PATTERN.sub("-", name.lower()).strip("-")


def ship_type_id(ship_type: Any) -> str:
    """Create a campaign-friendly ID from a pydcs ship type."""

    return PYDCS_ID_PATTERN.sub("-", ship_type.id.lower()).strip("-")


def dcs_point_from_pydcs(point: Any) -> DcsPoint:
    """Convert a pydcs point into the local immutable point type."""

    return DcsPoint(x=point.x, y=point.y)


def atc_radio_payload(atc_radio: Any | None) -> dict[str, int] | None:
    """Return JSON-friendly ATC radio data from pydcs."""

    if atc_radio is None:
        return None
    return {
        "hf_hz": atc_radio.hf_hz,
        "vhf_low_hz": atc_radio.vhf_low_hz,
        "vhf_high_hz": atc_radio.vhf_high_hz,
        "uhf_hz": atc_radio.uhf_hz,
    }


def runway_approach_payload(approach: Any) -> dict[str, Any]:
    """Return a runway end from pydcs."""

    return {"name": approach.name, "heading": approach.heading}


def runway_payload(runway: Any) -> dict[str, Any]:
    """Return JSON-friendly runway data from pydcs."""

    return {
        "id": runway.id,
        "name": runway.name,
        "heading": runway.main.heading,
        "main": runway_approach_payload(runway.main),
        "opposite": runway_approach_payload(runway.opposite),
    }


def parking_slot_payload(slot: Any) -> dict[str, Any]:
    """Return JSON-friendly parking slot data from pydcs."""

    point = dcs_point_from_pydcs(slot.position)
    return {
        "id": slot.crossroad_idx,
        "name": slot.slot_name,
        "point": {"x": point.x, "y": point.y},
        "large": slot.large,
        "helicopter": slot.helicopter,
        "airplanes": slot.airplanes,
        "length": slot.length,
        "width": slot.width,
        "height": slot.height,
        "shelter": slot.shelter,
    }


def airbase_from_pydcs(airport: Any) -> dict[str, Any]:
    """Return local theater airbase data from a pydcs airport."""

    return {
        "id": airbase_id(airport.name),
        "dcs_airport_id": airport.id,
        "name": airport.name,
        "category": "civilian" if airport.civilian else "military",
        "point": dcs_point_from_pydcs(airport.position),
        "runways": [runway_payload(runway) for runway in airport.runways],
        "parking_slots": len(airport.parking_slots),
        "parking": [parking_slot_payload(slot) for slot in airport.parking_slots],
        "atc_radio": atc_radio_payload(airport.atc_radio),
        "frequencies": list(airport.frequencies),
    }


def airbases_from_pydcs(terrain: Any) -> tuple[dict[str, Any], ...]:
    """Return all pydcs terrain airports as local airbase payloads."""

    return tuple(airbase_from_pydcs(airport) for airport in terrain.airports.values())


def ship_type_from_pydcs(ship_type: Any) -> ShipTypeDefinition:
    """Return local ship metadata from a pydcs ship type."""

    return ShipTypeDefinition(
        id=ship_type_id(ship_type),
        display_name=ship_type.name,
        dcs_type_name=ship_type.id,
        plane_capacity=getattr(ship_type, "plane_num", 0),
        helicopter_capacity=getattr(ship_type, "helicopter_num", 0),
        parking_slots=getattr(ship_type, "parking", 0),
        detection_range_m=getattr(ship_type, "detection_range", 0),
        threat_range_m=getattr(ship_type, "threat_range", 0),
        air_weapon_distance_m=getattr(ship_type, "air_weapon_dist", 0),
    )
