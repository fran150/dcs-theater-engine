from __future__ import annotations

import asyncio
import json
from typing import Any

from dcs_theater_engine.api.app import create_app


def request_json(
    method: str,
    path: str,
    payload: dict[str, Any] | None = None,
) -> tuple[int, str]:
    async def request() -> tuple[int, str]:
        app = create_app()
        messages: list[dict[str, Any]] = []
        body = json.dumps(payload or {}).encode()

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": body, "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": method,
                "scheme": "http",
                "path": path,
                "raw_path": path.encode(),
                "query_string": b"",
                "headers": [(b"content-type", b"application/json")],
                "client": ("testclient", 50000),
                "server": ("testserver", 80),
            },
            receive,
            send,
        )

        status = next(
            message["status"]
            for message in messages
            if message["type"] == "http.response.start"
        )
        body = b"".join(
            message.get("body", b"")
            for message in messages
            if message["type"] == "http.response.body"
        )
        return status, body.decode()

    return asyncio.run(request())


def get(path: str) -> tuple[int, str]:
    return request_json("GET", path)


def post(path: str, payload: dict[str, Any]) -> tuple[int, str]:
    return request_json("POST", path, payload)


def test_marianas_map_payload_is_served() -> None:
    status, body = get("/api/theaters/marianas/map")

    assert status == 200
    payload = json.loads(body)
    assert payload["id"] == "marianas"
    assert payload["name"] == "Mariana Islands"
    assert len(payload["airbases"]) == 8
    assert any(
        airbase["name"] == "Andersen AFB" for airbase in payload["airbases"]
    )


def test_index_serves_map_ui() -> None:
    status, body = get("/")

    assert status == 200
    assert "DCS Theater Engine" in body
    assert "/static/app.js" in body
    assert "leaflet@1.9.4" in body
    assert 'id="mapCanvas"' in body


def test_campaign_runtime_snapshot_is_served() -> None:
    status, body = get("/api/campaign/runtime")

    assert status == 200
    payload = json.loads(body)
    assert payload["campaign_name"] == "Marianas Continuous Campaign"
    assert payload["theater_id"] == "marianas"
    assert payload["time_scale"] == 1
    assert payload["running"] is True
    assert "mission_scheduler" in payload["systems"]
    assert len(payload["airbases"]) == 8


def test_campaign_runtime_time_scale_can_be_changed() -> None:
    status, body = post("/api/campaign/runtime/time-scale", {"time_scale": 16})

    assert status == 200
    payload = json.loads(body)
    assert payload["time_scale"] == 16
    assert payload["recent_events"][-1]["event_type"] == "time_scale_changed"


def test_campaign_runtime_rejects_invalid_time_scale() -> None:
    status, body = post("/api/campaign/runtime/time-scale", {"time_scale": 8})

    assert status == 400
    assert "1, 2, 4, 16, 32, 64" in body


def test_campaign_runtime_rejects_missing_time_scale() -> None:
    status, body = post("/api/campaign/runtime/time-scale", {})

    assert status == 400
    assert "time_scale" in body


def test_campaign_runtime_rejects_non_integer_time_scale() -> None:
    status, body = post(
        "/api/campaign/runtime/time-scale",
        {"time_scale": "16"},
    )

    assert status == 400
    assert "time_scale" in body
