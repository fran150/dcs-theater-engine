"""Campaign coalition definitions."""

from __future__ import annotations

from enum import StrEnum


class Coalition(StrEnum):
    """Campaign coalitions."""

    BLUE = "blue"
    RED = "red"
    NEUTRAL = "neutral"
