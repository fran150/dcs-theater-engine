"""FastAPI dependencies for route modules."""

from __future__ import annotations

from fastapi import Request

from dcs_theater_engine.campaign.runtime import CampaignRuntimeService


def get_campaign_runtime(request: Request) -> CampaignRuntimeService:
    """Return the application-scoped campaign runtime service."""

    return request.app.state.campaign_runtime
