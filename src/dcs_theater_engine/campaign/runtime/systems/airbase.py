"""Airbase runtime systems."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from dcs_theater_engine.campaign.core import CampaignState


@dataclass(slots=True)
class AirbaseRepairSystem:
    """Slowly repair runway damage while the campaign clock is running."""

    repair_per_hour: float = 0.02
    name: str = "airbase_repair"

    def update(self, state: CampaignState, delta: timedelta) -> None:
        if delta.total_seconds() <= 0:
            return

        repaired = self.repair_per_hour * (delta.total_seconds() / 3600)
        for _, airbase in state.airbase_items():
            airbase.runway_damage = max(0.0, airbase.runway_damage - repaired)
