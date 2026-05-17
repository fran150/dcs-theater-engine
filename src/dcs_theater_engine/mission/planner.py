"""Campaign mission planning and scheduling."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import uuid4

from dcs_theater_engine.commander.api import MissionRequest
from dcs_theater_engine.events import EventType


class MissionStatus(StrEnum):
    """Lifecycle state for campaign missions."""

    PLANNED = "planned"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass(slots=True)
class CampaignMission:
    """A planned or active campaign-level mission."""

    request: MissionRequest
    scheduled_start: datetime
    id: str = field(default_factory=lambda: str(uuid4()))
    status: MissionStatus = MissionStatus.PLANNED


@dataclass(slots=True)
class CampaignMissionPlanner:
    """Turns commander intent into valid campaign missions."""

    missions: dict[str, CampaignMission] = field(default_factory=dict)

    def plan(self, request: MissionRequest, start_time: datetime) -> CampaignMission:
        """Create a minimal planned mission from a validated request."""

        mission = CampaignMission(request=request, scheduled_start=start_time)
        self.missions[mission.id] = mission
        return mission

    def launch_due_missions(self, current_time: datetime) -> list[CampaignMission]:
        """Mark planned missions active when their scheduled time arrives."""

        launched: list[CampaignMission] = []
        for mission in self.missions.values():
            if (
                mission.status == MissionStatus.PLANNED
                and mission.scheduled_start <= current_time
            ):
                mission.status = MissionStatus.ACTIVE
                launched.append(mission)
        return launched

    @staticmethod
    def planned_event_payload(mission: CampaignMission) -> dict[str, object]:
        """Return event payload for mission planning."""

        return {
            "mission_id": mission.id,
            "mission_type": mission.request.mission_type,
            "coalition": mission.request.coalition,
            "event_type": EventType.MISSION_PLANNED,
        }

