"""Airbase static data definitions."""

from __future__ import annotations

from dataclasses import dataclass

from dcs_theater_engine.data.coordinates import DcsPoint


@dataclass(frozen=True, slots=True)
class AirbaseData:
    """Static airbase metadata.

    Attributes:
        id: Stable local identifier for the airbase.
        name: Display name for the airbase.
        position: DCS world position for the airbase.
        dcs_airport_id: Optional pydcs airport identifier for simulator mapping.
    """

    id: str
    name: str
    position: DcsPoint
    dcs_airport_id: int | None = None
