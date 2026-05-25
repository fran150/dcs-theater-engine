from __future__ import annotations

import asyncio
import json
from typing import Any

import pytest

from dcs_theater_engine.api.app import create_app
from dcs_theater_engine.data.coordinates import DcsPoint
from dcs_theater_engine.data.marianas import MARIANAS_PROJECTION


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
    assert len(payload["carrier_groups"]) == 2
    assert payload["bounds"]["xMin"] == -300000
    assert payload["bounds"]["xMax"] == 1000000
    assert len(payload["bounds"]["outline"]) > 4
    andersen = next(
        airbase
        for airbase in payload["airbases"]
        if airbase["name"] == "Andersen AFB"
    )
    assert andersen["id"] == "andersen-afb"
    assert andersen["dcs_airport_id"] == 6
    assert [runway["name"] for runway in andersen["runways"]] == [
        "06L-24R",
        "06R-24L",
    ]
    assert andersen["parking_slots"] == 194
    assert len(andersen["parking"]) == 194
    assert andersen["atc_radio"]["uhf_hz"] == 250100000
    us_group = next(
        group
        for group in payload["carrier_groups"]
        if group["id"] == "us-carrier-group-southeast"
    )
    assert us_group["coalition"] == "blue"
    assert us_group["point"] == {"x": -160000, "y": 260000}
    assert us_group["ships"][0]["ship_type"]["dcs_type_name"] == "Stennis"
    russian_group = next(
        group
        for group in payload["carrier_groups"]
        if group["id"] == "russian-carrier-group-northwest"
    )
    assert russian_group["coalition"] == "red"
    assert russian_group["point"] == {"x": 650000, "y": -180000}
    assert russian_group["ships"][0]["ship_type"]["dcs_type_name"] == "KUZNECOW"


def test_marianas_projection_derives_wgs84_from_dcs_points() -> None:
    point = DcsPoint(x=10574.989746, y=14548.833496)

    lat_lon = MARIANAS_PROJECTION.to_lat_lon(point)
    round_trip = MARIANAS_PROJECTION.to_dcs_point(lat_lon)

    assert lat_lon.latitude == pytest.approx(13.58170286)
    assert lat_lon.longitude == pytest.approx(144.93105130)
    assert round_trip.x == pytest.approx(point.x)
    assert round_trip.y == pytest.approx(point.y)


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
