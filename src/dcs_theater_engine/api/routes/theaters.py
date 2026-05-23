"""Theater data API routes."""

from __future__ import annotations

from fastapi import APIRouter

from dcs_theater_engine.data.marianas import marianas_map_payload

# Group theater data endpoints under their shared API prefix.
router = APIRouter(prefix="/api/theaters", tags=["theaters"])


@router.get("/marianas/map")
def marianas_map() -> dict[str, object]:
    # Serve the static Marianas theater map data used by the browser UI.
    return marianas_map_payload()
