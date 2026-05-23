"""Intelligence runtime systems."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from dcs_theater_engine.campaign.core import CampaignState


@dataclass(slots=True)
class IntelligenceSystem:
    """Placeholder for detection, stale contacts, and coalition intel views."""

    name: str = "intelligence"

    def update(self, state: CampaignState, delta: timedelta) -> None:
        return
