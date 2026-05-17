from datetime import UTC, datetime, timedelta

from dcs_theater_engine.campaign import CampaignSimulator, CampaignState
from dcs_theater_engine.campaign.core import AirbaseState, Coalition
from dcs_theater_engine.events import EventType
from dcs_theater_engine.persistence import load_campaign, save_campaign


def test_campaign_simulator_advances_time_and_records_event() -> None:
    state = CampaignState(
        name="Smoke Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 12, 0, tzinfo=UTC),
    )
    simulator = CampaignSimulator(state)

    simulator.advance(timedelta(minutes=10))

    assert state.current_time == datetime(2026, 5, 17, 12, 10, tzinfo=UTC)
    assert state.events[-1].event_type == EventType.TIME_ADVANCED


def test_campaign_state_round_trips_through_json(tmp_path) -> None:
    state = CampaignState(
        name="Persistence Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 12, 0, tzinfo=UTC),
    )
    airbase = AirbaseState(
        id="airbase-1",
        name="Test Airbase",
        coalition=Coalition.BLUE,
        definition_id="test-airbase",
        runway_damage=0.25,
    )
    state.airbases[airbase.id] = airbase
    state.record_event(EventType.CAMPAIGN_CREATED)

    save_path = tmp_path / "campaign.json"
    save_campaign(state, save_path)
    loaded = load_campaign(save_path)

    assert loaded.name == state.name
    assert loaded.current_time == state.current_time
    assert loaded.airbases["airbase-1"].runway_damage == 0.25
    assert loaded.events[0].event_type == EventType.CAMPAIGN_CREATED
