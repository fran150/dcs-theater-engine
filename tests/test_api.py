from __future__ import annotations

import asyncio
import json
from typing import Any

from dcs_theater_engine.api.app import create_app


def get(path: str) -> tuple[int, str]:
    async def request() -> tuple[int, str]:
        app = create_app()
        messages: list[dict[str, Any]] = []

        async def receive() -> dict[str, Any]:
            return {"type": "http.request", "body": b"", "more_body": False}

        async def send(message: dict[str, Any]) -> None:
            messages.append(message)

        await app(
            {
                "type": "http",
                "asgi": {"version": "3.0"},
                "http_version": "1.1",
                "method": "GET",
                "scheme": "http",
                "path": path,
                "raw_path": path.encode(),
                "query_string": b"",
                "headers": [],
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
