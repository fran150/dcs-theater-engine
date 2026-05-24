"""Static data definitions used to build campaigns."""

from __future__ import annotations

from dataclasses import dataclass, field

from dcs_theater_engine.data.coordinates import DcsPoint


@dataclass(frozen=True, slots=True)
class AircraftTypeDefinition:
    """Static aircraft metadata and DCS mapping."""

    id: str
    display_name: str
    dcs_type_name: str


@dataclass(frozen=True, slots=True)
class AirbaseDefinition:
    """Static airbase metadata."""

    id: str
    name: str
    position: DcsPoint
    dcs_airport_id: int | None = None


@dataclass(frozen=True, slots=True)
class TheaterDefinition:
    """Static theater metadata.

    Geometry fields intentionally start generic. They can later be replaced by
    richer GIS objects once we choose the file format.
    """

    id: str
    name: str
    airbases: tuple[AirbaseDefinition, ...] = ()
    land_polygons: tuple[tuple[DcsPoint, ...], ...] = ()
    sea_polygons: tuple[tuple[DcsPoint, ...], ...] = ()
    named_routes: dict[str, tuple[DcsPoint, ...]] = field(
        default_factory=dict
    )
