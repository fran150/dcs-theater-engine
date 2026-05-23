"""Campaign scenario initializers."""

from __future__ import annotations

from datetime import UTC, datetime

from dcs_theater_engine.campaign.core import (
    AirbaseState,
    CampaignState,
    Coalition,
    SquadronState,
)
from dcs_theater_engine.data.marianas import MARIANAS_THEATER
from dcs_theater_engine.events import EventType


def create_marianas_campaign() -> CampaignState:
    """Create a small campaign seed for the Marianas theater."""

    state = CampaignState(
        name="Marianas Continuous Campaign",
        theater_id=MARIANAS_THEATER.id,
        current_time=datetime(2026, 5, 17, 12, 0, tzinfo=UTC),
    )

    for airbase in MARIANAS_THEATER.airbases:
        coalition = Coalition.BLUE if "guam" in airbase.id or airbase.id in {
            "andersen-afb",
            "antonio-b-won-pat-intl",
            "olf-orote",
            "north-west-field",
        } else Coalition.RED
        campaign_airbase = AirbaseState(
            id=airbase.id,
            name=airbase.name,
            coalition=coalition,
            definition_id=airbase.id,
        )
        state.airbases[campaign_airbase.id] = campaign_airbase

    state.squadrons["vfa-27"] = SquadronState(
        id="vfa-27",
        name="VFA-27 Royal Maces",
        coalition=Coalition.BLUE,
        aircraft_type="F/A-18C",
        home_airbase_id="andersen-afb",
        available_aircraft=12,
    )
    state.squadrons["18th-aggressor"] = SquadronState(
        id="18th-aggressor",
        name="18th Aggressor Squadron",
        coalition=Coalition.RED,
        aircraft_type="MiG-29S",
        home_airbase_id="saipan-intl",
        available_aircraft=8,
    )
    state.record_event(
        EventType.CAMPAIGN_CREATED,
        {"theater_id": state.theater_id, "mode": "coarse_campaign_steps"},
    )
    return state
