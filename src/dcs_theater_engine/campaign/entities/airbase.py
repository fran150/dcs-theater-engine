"""Airbase campaign entity components."""

from __future__ import annotations

from dataclasses import dataclass

from dcs_theater_engine.campaign.entities.coalition import Coalition


@dataclass(slots=True)
class AirbaseState:
    """Mutable component for an airbase campaign entity.

    Attributes:
        name: Display name for the airbase.
        coalition: Coalition currently controlling the airbase.
        definition_id: Static airbase definition this entity represents.
        runway_damage: Current runway damage from 0.0 to 1.0.
    """

    name: str
    coalition: Coalition
    definition_id: str
    runway_damage: float = 0.0
