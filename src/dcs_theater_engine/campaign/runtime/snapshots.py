"""Serializable runtime views."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from dcs_theater_engine.campaign.core import AirbaseState, SquadronState
from dcs_theater_engine.events import CampaignEvent

if TYPE_CHECKING:
    from dcs_theater_engine.campaign.runtime.campaign import CampaignRuntime


@dataclass(slots=True)
class AirbaseSnapshot:
    """Serializable view of an airbase."""

    id: str
    name: str
    coalition: str
    definition_id: str
    runway_damage: float


@dataclass(slots=True)
class SquadronSnapshot:
    """Serializable view of a squadron."""

    id: str
    name: str
    coalition: str
    aircraft_type: str
    home_airbase_id: str
    available_aircraft: int
    damaged_aircraft: int


@dataclass(slots=True)
class EventSnapshot:
    """Serializable view of a campaign event."""

    id: str
    event_type: str
    campaign_time: str
    payload: dict[str, Any]


@dataclass(slots=True)
class RuntimeSnapshot:
    """Serializable view of the campaign runtime.

    Attributes:
        campaign_name: Display name for this campaign instance.
        theater_id: Static theater definition used by the campaign.
        campaign_time: Current campaign time as an ISO 8601 string.
        time_scale: Campaign pacing multiplier.
        running: Whether the campaign runtime is advancing.
        systems: Runtime systems registered with the campaign.
        airbases: Public airbase state.
        squadrons: Public squadron state.
        recent_events: Recent campaign event history.
    """

    campaign_name: str
    theater_id: str
    campaign_time: str
    time_scale: int
    running: bool
    systems: list[str]
    airbases: list[AirbaseSnapshot]
    squadrons: list[SquadronSnapshot]
    recent_events: list[EventSnapshot]


def build_runtime_snapshot(runtime: CampaignRuntime) -> RuntimeSnapshot:
    """Build the public runtime view from authoritative campaign state."""

    state = runtime.state
    return RuntimeSnapshot(
        campaign_name=state.name,
        theater_id=state.theater_id,
        campaign_time=state.current_time.isoformat(),
        time_scale=runtime.time_scale,
        running=runtime.running,
        systems=[system.name for system in runtime.systems],
        # Keep entity projection here so runtime logic stays focused on time.
        airbases=[airbase_snapshot(airbase) for airbase in state.airbases.values()],
        squadrons=[
            squadron_snapshot(squadron) for squadron in state.squadrons.values()
        ],
        recent_events=[event_snapshot(event) for event in state.events[-10:]],
    )


def airbase_snapshot(airbase: AirbaseState) -> AirbaseSnapshot:
    """Build the public view of one airbase."""

    return AirbaseSnapshot(
        id=airbase.id,
        name=airbase.name,
        coalition=airbase.coalition.value,
        definition_id=airbase.definition_id,
        runway_damage=airbase.runway_damage,
    )


def squadron_snapshot(squadron: SquadronState) -> SquadronSnapshot:
    """Build the public view of one squadron."""

    return SquadronSnapshot(
        id=squadron.id,
        name=squadron.name,
        coalition=squadron.coalition.value,
        aircraft_type=squadron.aircraft_type,
        home_airbase_id=squadron.home_airbase_id,
        available_aircraft=squadron.available_aircraft,
        damaged_aircraft=squadron.damaged_aircraft,
    )


def event_snapshot(event: CampaignEvent) -> EventSnapshot:
    """Build the public view of one campaign event."""

    return EventSnapshot(
        id=event.id,
        event_type=event.event_type.value,
        campaign_time=event.campaign_time.isoformat(),
        payload=dict(event.payload),
    )
