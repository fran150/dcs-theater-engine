"""Naval static data definitions."""

from __future__ import annotations

from dataclasses import dataclass

from dcs.unittype import ShipType

from dcs_theater_engine.data.coordinates import DcsPoint


@dataclass(frozen=True, slots=True)
class ShipData:
    """Static ship placement inside a naval group.

    Attributes:
        id: Stable local identifier for the ship.
        name: Display name for the ship.
        ship_type: pydcs ship type class for this ship.
        position: DCS world position for the ship.
        heading: Initial ship heading in degrees.
    """

    id: str
    name: str
    ship_type: type[ShipType]
    position: DcsPoint
    heading: float


@dataclass(frozen=True, slots=True)
class CarrierGroupData:
    """Static carrier group metadata.

    Attributes:
        id: Stable local identifier for the carrier group.
        name: Display name for the carrier group.
        country: DCS country name used for generated group ownership.
        coalition: Coalition name used when seeding campaign state.
        position: DCS world position for the group.
        heading: Initial group heading in degrees.
        ships: Ships that make up this carrier group.
    """

    id: str
    name: str
    country: str
    coalition: str
    position: DcsPoint
    heading: float
    ships: tuple[ShipData, ...] = ()
