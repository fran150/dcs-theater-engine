"""Browser UI routes."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

from dcs_theater_engine.api.config import STATIC_DIR

# Root UI routes do not need an API prefix.
router = APIRouter()


@router.get("/", include_in_schema=False)
def index() -> HTMLResponse:
    # Serve the single-page browser UI entrypoint.
    return HTMLResponse((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
