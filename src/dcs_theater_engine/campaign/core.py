"""Mutable campaign state."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from dcs_theater_engine.events import CampaignEvent, EventType


class Coalition(StrEnum):
    """Campaign coalitions."""

    BLUE = "blue"
    RED = "red"
    NEUTRAL = "neutral"


@dataclass(slots=True)
class AirbaseState:
    """Mutable state for an airbase in a campaign instance."""

    name: str
    coalition: Coalition
    definition_id: str
    id: str = field(default_factory=lambda: str(uuid4()))
    runway_damage: float = 0.0


@dataclass(slots=True)
class SquadronState:
    """Mutable state for a squadron in a campaign instance."""

    name: str
    coalition: Coalition
    aircraft_type: str
    home_airbase_id: str
    available_aircraft: int
    id: str = field(default_factory=lambda: str(uuid4()))
    damaged_aircraft: int = 0


@dataclass(slots=True)
class CampaignState:
    """Authoritative mutable state for one campaign run.

    Attributes:
        name: Display name for this campaign instance.
        theater_id: Static theater definition used by the campaign.
        current_time: Current campaign time.
        airbases: Mutable airbase state keyed by campaign airbase ID.
        squadrons: Mutable squadron state keyed by squadron ID.
        events: Campaign event history.
    """

    name: str
    theater_id: str
    current_time: datetime
    airbases: dict[str, AirbaseState] = field(default_factory=dict)
    squadrons: dict[str, SquadronState] = field(default_factory=dict)
    events: list[CampaignEvent] = field(default_factory=list)

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
