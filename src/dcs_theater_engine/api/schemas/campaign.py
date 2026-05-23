"""Campaign API schemas."""

from __future__ import annotations

from pydantic import BaseModel, StrictInt


class TimeScaleRequest(BaseModel):
    """Request body for changing the campaign time multiplier."""

    # Require a real integer so strings like "16" are rejected by validation.
    time_scale: StrictInt
