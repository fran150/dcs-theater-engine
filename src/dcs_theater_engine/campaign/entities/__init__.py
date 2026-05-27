"""Campaign entity component definitions."""

from dcs_theater_engine.campaign.entities.airbase import AirbaseState
from dcs_theater_engine.campaign.entities.coalition import Coalition
from dcs_theater_engine.campaign.entities.squadron import (
    HOME_AIRBASE_RELATION,
    SquadronState,
)

__all__ = [
    "AirbaseState",
    "Coalition",
    "HOME_AIRBASE_RELATION",
    "SquadronState",
]
