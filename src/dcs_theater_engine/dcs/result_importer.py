"""DCS result import boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from dcs_theater_engine.campaign.core import CampaignState
from dcs_theater_engine.events import EventType


@dataclass(frozen=True, slots=True)
class DcsResultImporter:
    """Reconciles DCS mission results back into campaign state."""

    def import_result(
        self, state: CampaignState, mission_id: str, result: dict[str, Any]
    ) -> None:
        """Record a minimal imported mission result."""

        state.record_event(
            EventType.MISSION_COMPLETED,
            {"mission_id": mission_id, "result": result},
        )

