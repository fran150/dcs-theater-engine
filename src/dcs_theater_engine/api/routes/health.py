"""System health routes."""

from __future__ import annotations

from fastapi import APIRouter

from dcs_theater_engine import __version__

# Keep system-level endpoints separate from gameplay API routes.
router = APIRouter(tags=["system"])


@router.get("/health")
def health() -> dict[str, str]:
    # Return a lightweight status response for probes and smoke tests.
    return {"status": "ok", "version": __version__}
