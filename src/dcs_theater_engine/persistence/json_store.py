"""JSON campaign save/load helpers."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from dcs_theater_engine.campaign.core import (
    AirbaseState,
    CampaignState,
    Coalition,
    SquadronState,
)
from dcs_theater_engine.events import CampaignEvent, EventType


def save_campaign(state: CampaignState, path: str | Path) -> None:
    """Save campaign state as human-readable JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(_campaign_to_dict(state), indent=2, sort_keys=True),
        encoding="utf-8",
    )


def load_campaign(path: str | Path) -> CampaignState:
    """Load campaign state from JSON."""

    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return _campaign_from_dict(payload)


def _campaign_to_dict(state: CampaignState) -> dict[str, Any]:
    return {
        "name": state.name,
        "theater_id": state.theater_id,
        "current_time": state.current_time.isoformat(),
        "airbases": {
            entity_id: {
                "id": airbase.id,
                "name": airbase.name,
                "coalition": airbase.coalition,
                "definition_id": airbase.definition_id,
                "runway_damage": airbase.runway_damage,
            }
            for entity_id, airbase in state.airbases.items()
        },
        "squadrons": {
            entity_id: {
                "id": squadron.id,
                "name": squadron.name,
                "coalition": squadron.coalition,
                "aircraft_type": squadron.aircraft_type,
                "home_airbase_id": squadron.home_airbase_id,
                "available_aircraft": squadron.available_aircraft,
                "damaged_aircraft": squadron.damaged_aircraft,
            }
            for entity_id, squadron in state.squadrons.items()
        },
        "events": [
            {
                "id": event.id,
                "event_type": event.event_type,
                "campaign_time": event.campaign_time.isoformat(),
                "created_at": event.created_at.isoformat(),
                "payload": event.payload,
            }
            for event in state.events
        ],
    }


def _campaign_from_dict(payload: dict[str, Any]) -> CampaignState:
    state = CampaignState(
        name=payload["name"],
        theater_id=payload["theater_id"],
        current_time=datetime.fromisoformat(payload["current_time"]),
    )

    state.airbases.update(
        {
            entity_id: AirbaseState(
                id=airbase["id"],
                name=airbase["name"],
                coalition=Coalition(airbase["coalition"]),
                definition_id=airbase["definition_id"],
                runway_damage=airbase["runway_damage"],
            )
            for entity_id, airbase in payload.get("airbases", {}).items()
        }
    )
    state.squadrons.update(
        {
            entity_id: SquadronState(
                id=squadron["id"],
                name=squadron["name"],
                coalition=Coalition(squadron["coalition"]),
                aircraft_type=squadron["aircraft_type"],
                home_airbase_id=squadron["home_airbase_id"],
                available_aircraft=squadron["available_aircraft"],
                damaged_aircraft=squadron["damaged_aircraft"],
            )
            for entity_id, squadron in payload.get("squadrons", {}).items()
        }
    )
    state.events.extend(
        CampaignEvent(
            id=event["id"],
            event_type=EventType(event["event_type"]),
            campaign_time=datetime.fromisoformat(event["campaign_time"]),
            created_at=datetime.fromisoformat(event["created_at"]),
            payload=event["payload"],
        )
        for event in payload.get("events", [])
    )
    return state

