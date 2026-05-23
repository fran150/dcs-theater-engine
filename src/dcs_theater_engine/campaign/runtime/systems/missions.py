"""Mission runtime systems."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from dcs_theater_engine.campaign.core import CampaignState


@dataclass(slots=True)
class MissionSchedulerSystem:
    """Placeholder for launching and updating scheduled campaign missions."""

    name: str = "mission_scheduler"

    def update(self, state: CampaignState, delta: timedelta) -> None:
        return
