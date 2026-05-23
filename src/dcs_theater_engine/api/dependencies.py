"""FastAPI dependencies for route modules."""

from __future__ import annotations

from fastapi import Request

from dcs_theater_engine.campaign.runtime import CampaignRuntime


def get_campaign_runtime(request: Request) -> CampaignRuntime:
    """Return the application-scoped campaign runtime."""

    return request.app.state.campaign_runtime
