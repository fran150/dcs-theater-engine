"""Mutable campaign state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Final

import tcod.ecs

from dcs_theater_engine.events import CampaignEvent, EventType

HOME_AIRBASE_RELATION: Final = "home_airbase"


class Coalition(StrEnum):
    """Campaign coalitions."""

    BLUE = "blue"
    RED = "red"
    NEUTRAL = "neutral"


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


@dataclass(slots=True)
class CampaignState:
    """Authoritative mutable state for one campaign run.

    Attributes:
        name: Display name for this campaign instance.
        theater_id: Static theater definition used by the campaign.
        current_time: Current campaign time.
        registry: ECS registry containing campaign entities and components.
        events: Campaign event history.
    """

    name: str
    theater_id: str
    current_time: datetime
    registry: tcod.ecs.Registry = field(default_factory=tcod.ecs.Registry)
    events: list[CampaignEvent] = field(default_factory=list)

    def add_airbase(
        self, entity_id: str, airbase: AirbaseState
    ) -> tcod.ecs.Entity:
        """Create or update an airbase entity."""

        entity = self.registry[entity_id]
        entity.components[AirbaseState] = airbase
        return entity

    def add_squadron(
        self,
        entity_id: str,
        squadron: SquadronState,
        home_airbase_id: str,
    ) -> tcod.ecs.Entity:
        """Create or update a squadron entity with its home-base relation."""

        entity = self.registry[entity_id]
        entity.components[SquadronState] = squadron
        entity.relation_tag[HOME_AIRBASE_RELATION] = self.registry[home_airbase_id]
        return entity

    def airbase_items(self) -> list[tuple[tcod.ecs.Entity, AirbaseState]]:
        """Return airbase entities with their mutable components."""

        return sorted(
            self.registry.Q[tcod.ecs.Entity, AirbaseState],
            key=lambda item: str(item[0].uid),
        )

    def squadron_items(self) -> list[tuple[tcod.ecs.Entity, SquadronState]]:
        """Return squadron entities with their mutable components."""

        return sorted(
            self.registry.Q[tcod.ecs.Entity, SquadronState],
            key=lambda item: str(item[0].uid),
        )

    def home_airbase_id(self, squadron_entity: tcod.ecs.Entity) -> str:
        """Return the home airbase ID for a squadron entity."""

        return str(squadron_entity.relation_tag[HOME_AIRBASE_RELATION].uid)

    def record_event(
        self, event_type: EventType, payload: dict[str, object] | None = None
    ) -> CampaignEvent:
        """Append an event to campaign history."""

        event = CampaignEvent(
            event_type=event_type,
            campaign_time=self.current_time,
            payload=dict(payload or {}),
        )
        self.events.append(event)
        return event
