"""Campaign runtime API routes."""

from __future__ import annotations

from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends

from dcs_theater_engine.api.dependencies import get_campaign_runtime
from dcs_theater_engine.api.schemas import TimeScaleRequest
from dcs_theater_engine.campaign.runtime import (
    ALLOWED_TIME_SCALES,
    CampaignRuntimeService,
)

# Group campaign endpoints under a shared API prefix and documentation tag.
router = APIRouter(prefix="/api/campaign", tags=["campaign"])

# Reuse the campaign runtime service dependency without repeating FastAPI wiring.
CampaignRuntimeServiceDep = Annotated[
    CampaignRuntimeService,
    Depends(get_campaign_runtime),
]


@router.get("/runtime")
def campaign_runtime(runtime: CampaignRuntimeServiceDep) -> dict[str, object]:
    # Return the latest serializable view of the running campaign.
    return asdict(runtime.snapshot())


@router.post("/runtime/time-scale")
def set_time_scale(
    payload: TimeScaleRequest,
    runtime: CampaignRuntimeServiceDep,
) -> dict[str, object]:
    # Let the runtime validate campaign rules; API handlers format any errors.
    runtime.set_time_scale(payload.time_scale)

    # Return the updated runtime snapshot so the UI can refresh immediately.
    return asdict(runtime.snapshot())


@router.get("/runtime/time-scales")
def campaign_time_scales() -> dict[str, object]:
    # Tell clients which time multipliers are currently supported.
    return {"allowed_time_scales": ALLOWED_TIME_SCALES}
