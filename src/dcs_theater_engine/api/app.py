"""FastAPI application factory."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from dcs_theater_engine import __version__
from dcs_theater_engine.api.config import STATIC_DIR
from dcs_theater_engine.api.errors import register_exception_handlers
from dcs_theater_engine.api.routes import ROUTERS
from dcs_theater_engine.campaign.runtime import CampaignRuntime, CampaignRuntimeService
from dcs_theater_engine.campaign.scenarios import create_marianas_campaign

CAMPAIGN_RUNTIME_TICK_INTERVAL_SECONDS = 0.25


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Run the campaign clock independently of API polling."""

    tick_task = asyncio.create_task(_run_campaign_runtime(app.state.campaign_runtime))
    try:
        yield
    finally:
        tick_task.cancel()
        with suppress(asyncio.CancelledError):
            await tick_task


async def _run_campaign_runtime(runtime: CampaignRuntimeService) -> None:
    while True:
        runtime.tick()
        await asyncio.sleep(CAMPAIGN_RUNTIME_TICK_INTERVAL_SECONDS)


def create_app() -> FastAPI:
    """Create the campaign API application."""

    # Build the root FastAPI object and store the active campaign runtime service
    # on app.state so route modules and lifespan tasks can use it.
    app = FastAPI(title="DCS Theater Engine", version=__version__, lifespan=lifespan)
    app.state.campaign_runtime = CampaignRuntimeService(
        CampaignRuntime(create_marianas_campaign())
    )

    # Register API-wide validation and domain error formatting.
    register_exception_handlers(app)

    # Serve browser assets like JavaScript and CSS from the packaged static folder.
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    # Attach each route module to the app while keeping endpoint code out of here.
    for router in ROUTERS:
        app.include_router(router)

    return app
