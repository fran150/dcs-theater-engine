"""Public API shape for doctrine and commander scripts."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from dcs_theater_engine.campaign.core import Coalition
from dcs_theater_engine.intelligence.fog import IntelligencePicture


class RequestedMissionType(StrEnum):
    """Mission intents a commander can request."""

    STRIKE = "strike"
    CAP = "cap"
    INTERCEPT = "intercept"
    RECON = "recon"


@dataclass(frozen=True, slots=True)
class MissionRequest:
    """Intent emitted by a commander or user script."""

    coalition: Coalition
    mission_type: RequestedMissionType
    target_id: str | None = None
    priority: int = 0


@dataclass(frozen=True, slots=True)
class CommanderContext:
    """Bounded information exposed to commander logic."""

    coalition: Coalition
    intelligence: IntelligencePicture

