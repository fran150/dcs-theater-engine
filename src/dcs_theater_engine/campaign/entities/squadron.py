"""Squadron campaign entity components."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from dcs_theater_engine.campaign.entities.coalition import Coalition

HOME_AIRBASE_RELATION: Final = "home_airbase"


@dataclass(slots=True)
class SquadronState:
    """Mutable component for a squadron campaign entity.

    Attributes:
        name: Display name for the squadron.
        coalition: Coalition this squadron belongs to.
        aircraft_type: Static aircraft type ID used by this squadron.
        available_aircraft: Flyable aircraft currently available.
        damaged_aircraft: Aircraft awaiting repair or replacement.
    """

    name: str
    coalition: Coalition
    aircraft_type: str
    available_aircraft: int
    damaged_aircraft: int = 0
