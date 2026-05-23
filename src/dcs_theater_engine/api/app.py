"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from dcs_theater_engine import __version__
from dcs_theater_engine.api.config import STATIC_DIR
from dcs_theater_engine.api.errors import register_exception_handlers
from dcs_theater_engine.api.routes import ROUTERS
from dcs_theater_engine.campaign.runtime import CampaignRuntime
from dcs_theater_engine.campaign.scenarios import create_marianas_campaign


def create_app() -> FastAPI:
    """Create the campaign API application."""

    # Build the root FastAPI object and store the active campaign runtime
    # on app.state so route modules can use it.
    app = FastAPI(title="DCS Theater Engine", version=__version__)
    app.state.campaign_runtime = CampaignRuntime(create_marianas_campaign())

    # Register API-wide validation and domain error formatting.
    register_exception_handlers(app)

    # Serve browser assets like JavaScript and CSS from the packaged static folder.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Attach each route module to the app while keeping endpoint code out of here.
    for router in ROUTERS:
        app.include_router(router)

    return app
