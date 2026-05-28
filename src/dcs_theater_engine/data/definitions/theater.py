"""Theater static data definitions."""

from __future__ import annotations

from dataclasses import dataclass, field

from dcs_theater_engine.data.coordinates import DcsPoint
from dcs_theater_engine.data.definitions.airbase import AirbaseData
from dcs_theater_engine.data.definitions.naval import CarrierGroupData


@dataclass(frozen=True, slots=True)
class TheaterData:
    """Static theater metadata.

    Geometry fields intentionally start generic. They can later be replaced by
    richer GIS objects once we choose the file format.

    Attributes:
        id: Stable local identifier for the theater.
        name: Display name for the theater.
        airbases: Static airbases available in this theater.
        carrier_groups: Static carrier groups available in this theater.
        land_polygons: DCS world-coordinate polygons for land regions.
        sea_polygons: DCS world-coordinate polygons for sea regions.
        named_routes: Named DCS world-coordinate route definitions.
    """

    id: str
    name: str
    airbases: tuple[AirbaseData, ...] = ()
    carrier_groups: tuple[CarrierGroupData, ...] = ()
    land_polygons: tuple[tuple[DcsPoint, ...], ...] = ()
    sea_polygons: tuple[tuple[DcsPoint, ...], ...] = ()
    named_routes: dict[str, tuple[DcsPoint, ...]] = field(default_factory=dict)
