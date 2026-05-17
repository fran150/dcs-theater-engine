"""DCS mission generation boundary."""

from __future__ import annotations

from dataclasses import dataclass

from dcs_theater_engine.mission.planner import CampaignMission


@dataclass(frozen=True, slots=True)
class DcsMissionGenerator:
    """Converts campaign missions into DCS mission artifacts."""

    def describe(self, mission: CampaignMission) -> dict[str, str]:
        """Return minimal metadata for a future generated DCS mission."""

        return {
            "campaign_mission_id": mission.id,
            "mission_type": mission.request.mission_type,
            "status": mission.status,
        }

