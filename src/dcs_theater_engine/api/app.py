"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from dcs_theater_engine import __version__
from dcs_theater_engine.data.marianas import marianas_map_payload

STATIC_DIR = Path(__file__).resolve().parent.parent / "ui" / "static"


def create_app() -> FastAPI:
    """Create the campaign API application."""

    app = FastAPI(title="DCS Theater Engine", version=__version__)
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.get("/", include_in_schema=False)
    def index() -> HTMLResponse:
        return HTMLResponse(
            (STATIC_DIR / "index.html").read_text(encoding="utf-8")
        )

    @app.get("/api/theaters/marianas/map")
    def marianas_map() -> dict[str, object]:
        return marianas_map_payload()

    return app
