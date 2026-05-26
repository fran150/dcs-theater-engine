from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta

from dcs_theater_engine.campaign import (
    CampaignRuntime,
    CampaignState,
)
from dcs_theater_engine.campaign.core import (
    AirbaseState,
    Coalition,
    SquadronState,
)
from dcs_theater_engine.campaign.errors import InvalidTimeScaleError
from dcs_theater_engine.events import EventType
from dcs_theater_engine.persistence import load_campaign, save_campaign
from dcs_theater_engine.persistence.json_store import _from_json_value, _to_json_value


@dataclass(slots=True)
class PersistenceMetadataExample:
    visible: str
    private_note: str = field(default="runtime-only", metadata={"persist": False})
    renamed: int = field(default=0, metadata={"json_name": "renamed_value"})
    tuple_values: tuple[str, ...] = field(
        default=(),
        metadata={"to_json": list, "from_json": tuple},
    )


def test_persistence_metadata_controls_field_projection() -> None:
    example = PersistenceMetadataExample(
        visible="saved",
        private_note="do not write",
        renamed=7,
        tuple_values=("alpha", "bravo"),
    )

    payload = _to_json_value(example)
    loaded = _from_json_value(payload, PersistenceMetadataExample)

    assert payload == {
        "visible": "saved",
        "renamed_value": 7,
        "tuple_values": ["alpha", "bravo"],
    }
    assert loaded == PersistenceMetadataExample(
        visible="saved",
        renamed=7,
        tuple_values=("alpha", "bravo"),
    )


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


def test_campaign_runtime_advances_by_wall_time_and_scale() -> None:
    current_real_time = datetime(2026, 5, 17, 12, 0, tzinfo=UTC)

    def clock() -> datetime:
        return current_real_time

    state = CampaignState(
        name="Runtime Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 18, 0, tzinfo=UTC),
    )
    runtime = CampaignRuntime(state, clock=clock)
    runtime.set_time_scale(4)

    current_real_time += timedelta(seconds=15)
    campaign_delta = runtime.tick()

    assert campaign_delta == timedelta(seconds=60)
    assert state.current_time == datetime(2026, 5, 17, 18, 1, tzinfo=UTC)
    assert state.events[-1].event_type == EventType.TIME_SCALE_CHANGED


def test_campaign_runtime_waits_for_full_campaign_step() -> None:
    current_real_time = datetime(2026, 5, 17, 12, 0, tzinfo=UTC)

    def clock() -> datetime:
        return current_real_time

    state = CampaignState(
        name="Runtime Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 18, 0, tzinfo=UTC),
    )
    runtime = CampaignRuntime(
        state,
        systems=[],
        clock=clock,
        step_size=timedelta(seconds=10),
    )

    current_real_time += timedelta(seconds=5)
    assert runtime.tick() == timedelta()
    assert state.current_time == datetime(2026, 5, 17, 18, 0, tzinfo=UTC)

    current_real_time += timedelta(seconds=5)
    assert runtime.tick() == timedelta(seconds=10)
    assert state.current_time == datetime(2026, 5, 17, 18, 0, 10, tzinfo=UTC)


def test_campaign_runtime_runs_systems_once_per_campaign_step() -> None:
    current_real_time = datetime(2026, 5, 17, 12, 0, tzinfo=UTC)
    update_deltas: list[timedelta] = []

    def clock() -> datetime:
        return current_real_time

    class RecordingSystem:
        name = "recording"

        def update(self, state: CampaignState, delta: timedelta) -> None:
            update_deltas.append(delta)

    state = CampaignState(
        name="Runtime Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 18, 0, tzinfo=UTC),
    )
    runtime = CampaignRuntime(
        state,
        systems=[RecordingSystem()],
        clock=clock,
        step_size=timedelta(seconds=10),
    )

    current_real_time += timedelta(seconds=25)

    assert runtime.tick() == timedelta(seconds=20)
    assert update_deltas == [timedelta(seconds=10), timedelta(seconds=10)]
    assert state.current_time == datetime(2026, 5, 17, 18, 0, 20, tzinfo=UTC)


def test_campaign_runtime_rejects_unsupported_time_scale() -> None:
    state = CampaignState(
        name="Runtime Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 18, 0, tzinfo=UTC),
    )
    runtime = CampaignRuntime(state)

    try:
        runtime.set_time_scale(8)
    except InvalidTimeScaleError as exc:
        assert "1, 2, 4, 16, 32, 64" in str(exc)
    else:
        raise AssertionError("Expected invalid time scale to be rejected.")


def test_campaign_runtime_snapshot_projects_public_state() -> None:
    current_real_time = datetime(2026, 5, 17, 12, 0, tzinfo=UTC)

    def clock() -> datetime:
        return current_real_time

    state = CampaignState(
        name="Projection Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 18, 0, tzinfo=UTC),
    )
    airbase = AirbaseState(
        id="airbase-1",
        name="Test Airbase",
        coalition=Coalition.BLUE,
        definition_id="test-airbase",
        runway_damage=0.25,
    )
    squadron = SquadronState(
        id="squadron-1",
        name="Test Squadron",
        coalition=Coalition.RED,
        aircraft_type="MiG-29A",
        home_airbase_id=airbase.id,
        available_aircraft=8,
        damaged_aircraft=1,
    )
    state.airbases[airbase.id] = airbase
    state.squadrons[squadron.id] = squadron
    state.record_event(EventType.CAMPAIGN_CREATED)
    runtime = CampaignRuntime(state, systems=[], clock=clock)

    payload = asdict(runtime.snapshot())

    assert payload["airbases"][0]["coalition"] == "blue"
    assert payload["squadrons"][0]["coalition"] == "red"
    assert payload["recent_events"][0]["event_type"] == "campaign_created"


def test_campaign_runtime_snapshot_does_not_advance_time() -> None:
    current_real_time = datetime(2026, 5, 17, 12, 0, tzinfo=UTC)

    def clock() -> datetime:
        return current_real_time

    state = CampaignState(
        name="Runtime Test",
        theater_id="test-theater",
        current_time=datetime(2026, 5, 17, 18, 0, tzinfo=UTC),
    )
    runtime = CampaignRuntime(state, systems=[], clock=clock)
    current_real_time += timedelta(seconds=30)

    runtime.snapshot()

    assert state.current_time == datetime(2026, 5, 17, 18, 0, tzinfo=UTC)
