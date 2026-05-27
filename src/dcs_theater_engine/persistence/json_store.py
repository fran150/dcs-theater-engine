"""JSON campaign save/load helpers.

Dataclass fields can use metadata to shape persistence:
`persist=False`, `json_name`, `to_json`, and `from_json`.
"""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from types import UnionType
from typing import Any, Union, get_args, get_origin, get_type_hints

from dcs_theater_engine.campaign.core import CampaignState
from dcs_theater_engine.campaign.entities import (
    AirbaseState,
    SquadronState,
)
from dcs_theater_engine.events import CampaignEvent

PERSIST_KEY = "persist"
JSON_NAME_KEY = "json_name"
TO_JSON_KEY = "to_json"
FROM_JSON_KEY = "from_json"


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
        "current_time": _to_json_value(state.current_time),
        "entities": _entities_to_dict(state),
        "events": _to_json_value(state.events),
    }


def _campaign_from_dict(payload: dict[str, Any]) -> CampaignState:
    if "entities" not in payload:
        return _legacy_campaign_from_dict(payload)

    state = CampaignState(
        name=payload["name"],
        theater_id=payload["theater_id"],
        current_time=_from_json_value(payload["current_time"], datetime),
        events=_from_json_value(payload.get("events", []), list[CampaignEvent]),
    )
    entities = payload["entities"]
    for entity_id, entity_payload in entities.items():
        if "airbase" in entity_payload:
            state.add_airbase(
                entity_id,
                _from_json_value(entity_payload["airbase"], AirbaseState),
            )

    for entity_id, entity_payload in entities.items():
        if "squadron" in entity_payload:
            state.add_squadron(
                entity_id,
                _from_json_value(entity_payload["squadron"], SquadronState),
                home_airbase_id=entity_payload["home_airbase_id"],
            )

    return state


def _entities_to_dict(state: CampaignState) -> dict[str, Any]:
    entities: dict[str, Any] = {}
    for entity, airbase in state.airbase_items():
        entities.setdefault(str(entity.uid), {})["airbase"] = _to_json_value(airbase)

    for entity, squadron in state.squadron_items():
        entity_payload = entities.setdefault(str(entity.uid), {})
        entity_payload["squadron"] = _to_json_value(squadron)
        entity_payload["home_airbase_id"] = state.home_airbase_id(entity)

    return entities


def _legacy_campaign_from_dict(payload: dict[str, Any]) -> CampaignState:
    state = CampaignState(
        name=payload["name"],
        theater_id=payload["theater_id"],
        current_time=_from_json_value(payload["current_time"], datetime),
        events=_from_json_value(payload.get("events", []), list[CampaignEvent]),
    )

    for fallback_id, airbase_payload in payload.get("airbases", {}).items():
        component_payload = dict(airbase_payload)
        entity_id = str(component_payload.pop("id", fallback_id))
        state.add_airbase(
            entity_id,
            _from_json_value(component_payload, AirbaseState),
        )

    for fallback_id, squadron_payload in payload.get("squadrons", {}).items():
        component_payload = dict(squadron_payload)
        entity_id = str(component_payload.pop("id", fallback_id))
        home_airbase_id = component_payload.pop("home_airbase_id")
        state.add_squadron(
            entity_id,
            _from_json_value(component_payload, SquadronState),
            home_airbase_id=home_airbase_id,
        )

    return state


def _to_json_value(value: Any, metadata: Any = None) -> Any:
    field_serializer = _field_serializer(metadata)
    if field_serializer is not None:
        return _to_json_value(field_serializer(value))

    if is_dataclass(value):
        return {
            _field_json_name(field): _to_json_value(
                getattr(value, field.name),
                field.metadata,
            )
            for field in fields(value)
            if _field_is_persisted(field)
        }

    if isinstance(value, datetime):
        return value.isoformat()

    if isinstance(value, Enum):
        return value.value

    if isinstance(value, dict):
        return {
            _to_json_value(key): _to_json_value(item)
            for key, item in value.items()
        }

    if isinstance(value, list | tuple):
        return [_to_json_value(item) for item in value]

    return value


def _from_json_value(payload: Any, expected_type: Any, metadata: Any = None) -> Any:
    field_loader = _field_loader(metadata)
    if field_loader is not None:
        return field_loader(payload)

    if payload is None or expected_type is Any:
        return payload

    expected_type = _without_none(expected_type)
    origin = get_origin(expected_type)

    if origin is dict:
        key_type, value_type = get_args(expected_type)
        return {
            _from_json_value(key, key_type): _from_json_value(value, value_type)
            for key, value in payload.items()
        }

    if origin is list:
        (item_type,) = get_args(expected_type)
        return [_from_json_value(item, item_type) for item in payload]

    if origin is tuple:
        item_type = get_args(expected_type)[0]
        return tuple(_from_json_value(item, item_type) for item in payload)

    if expected_type is datetime:
        return datetime.fromisoformat(payload)

    if isinstance(expected_type, type) and issubclass(expected_type, Enum):
        return expected_type(payload)

    if isinstance(expected_type, type) and is_dataclass(expected_type):
        type_hints = get_type_hints(expected_type)
        kwargs = {
            field.name: _from_json_value(
                payload[_field_json_name(field)],
                type_hints[field.name],
                field.metadata,
            )
            for field in fields(expected_type)
            if _field_is_persisted(field) and _field_json_name(field) in payload
        }
        return expected_type(**kwargs)

    return payload


def _field_is_persisted(field: Any) -> bool:
    return field.metadata.get(PERSIST_KEY, True) is not False


def _field_json_name(field: Any) -> str:
    return field.metadata.get(JSON_NAME_KEY, field.name)


def _field_serializer(metadata: Any) -> Any:
    if metadata is None:
        return None
    return metadata.get(TO_JSON_KEY)


def _field_loader(metadata: Any) -> Any:
    if metadata is None:
        return None
    return metadata.get(FROM_JSON_KEY)


def _without_none(expected_type: Any) -> Any:
    origin = get_origin(expected_type)
    if origin not in (Union, UnionType):
        return expected_type

    args = tuple(arg for arg in get_args(expected_type) if arg is not NoneType)
    if len(args) == 1:
        return args[0]
    return expected_type


NoneType = type(None)
