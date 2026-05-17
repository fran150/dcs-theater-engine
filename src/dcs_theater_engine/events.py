"""Campaign event primitives."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class EventType(StrEnum):
    """Events that describe meaningful campaign changes."""

    CAMPAIGN_CREATED = "campaign_created"
    TIME_ADVANCED = "time_advanced"
    MISSION_PLANNED = "mission_planned"
    MISSION_LAUNCHED = "mission_launched"
    MISSION_COMPLETED = "mission_completed"
    UNIT_DETECTED = "unit_detected"
    UNIT_MOVED = "unit_moved"
    AIRCRAFT_DESTROYED = "aircraft_destroyed"
    OBJECTIVE_STRUCK = "objective_struck"
    INTEL_UPDATED = "intel_updated"


@dataclass(frozen=True, slots=True)
class CampaignEvent:
    """Append-only event emitted by campaign systems."""

    event_type: EventType
    campaign_time: datetime
    payload: dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

