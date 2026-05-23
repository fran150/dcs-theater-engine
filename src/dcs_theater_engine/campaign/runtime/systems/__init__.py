"""Runtime update systems."""

from dcs_theater_engine.campaign.runtime.systems.airbase import AirbaseRepairSystem
from dcs_theater_engine.campaign.runtime.systems.base import CampaignSystem
from dcs_theater_engine.campaign.runtime.systems.intelligence import IntelligenceSystem
from dcs_theater_engine.campaign.runtime.systems.missions import MissionSchedulerSystem


def default_campaign_systems() -> list[CampaignSystem]:
    """Return the initial campaign update pipeline."""

    return [MissionSchedulerSystem(), IntelligenceSystem(), AirbaseRepairSystem()]


__all__ = [
    "AirbaseRepairSystem",
    "CampaignSystem",
    "IntelligenceSystem",
    "MissionSchedulerSystem",
    "default_campaign_systems",
]
