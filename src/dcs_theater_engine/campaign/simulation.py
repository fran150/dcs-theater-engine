"""Campaign time advancement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from dcs_theater_engine.campaign.core import CampaignState
from dcs_theater_engine.events import EventType


@dataclass(slots=True)
class CampaignSimulator:
    """Advances campaign state outside DCS."""

    state: CampaignState

    def advance(self, delta: timedelta) -> None:
        """Advance campaign time and emit a minimal event."""

        if delta.total_seconds() <= 0:
            raise ValueError("Simulation delta must be positive.")

        previous_time = self.state.current_time
        self.state.current_time += delta
        self.state.record_event(
            EventType.TIME_ADVANCED,
            {
                "from": previous_time.isoformat(),
                "to": self.state.current_time.isoformat(),
                "seconds": delta.total_seconds(),
            },
        )

