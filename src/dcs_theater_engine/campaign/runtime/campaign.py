"""Coarse-step campaign runtime."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

from dcs_theater_engine.campaign.core import CampaignState
from dcs_theater_engine.campaign.errors import InvalidTimeScaleError
from dcs_theater_engine.campaign.runtime.snapshots import (
    RuntimeSnapshot,
    build_runtime_snapshot,
)
from dcs_theater_engine.campaign.runtime.systems import (
    CampaignSystem,
    default_campaign_systems,
)
from dcs_theater_engine.events import EventType

ALLOWED_TIME_SCALES = (1, 2, 4, 16, 32, 64)
DEFAULT_CAMPAIGN_STEP = timedelta(seconds=10)


@dataclass(slots=True)
class CampaignRuntime:
    """Owns paced campaign clock advancement."""

    state: CampaignState
    systems: list[CampaignSystem] = field(default_factory=default_campaign_systems)
    time_scale: int = 1
    running: bool = True
    clock: Callable[[], datetime] = field(
        default_factory=lambda: lambda: datetime.now(UTC), repr=False
    )
    step_size: timedelta = DEFAULT_CAMPAIGN_STEP
    _last_real_tick: datetime = field(init=False, repr=False)
    _pending_campaign_delta: timedelta = field(
        default_factory=timedelta, init=False, repr=False
    )

    def __post_init__(self) -> None:
        self._validate_time_scale(self.time_scale)
        if self.step_size <= timedelta():
            raise ValueError("Campaign step size must be positive.")
        self._last_real_tick = self.clock()

    def tick(self, now: datetime | None = None) -> timedelta:
        """Advance campaign time when enough paced time has accumulated."""

        current_real_time = now or self.clock()
        real_delta = current_real_time - self._last_real_tick
        self._last_real_tick = current_real_time

        if not self.running or real_delta.total_seconds() <= 0:
            return timedelta()

        self._pending_campaign_delta += real_delta * self.time_scale
        campaign_delta = self._next_campaign_delta()
        if campaign_delta <= timedelta():
            return timedelta()

        self.state.current_time += campaign_delta
        for system in self.systems:
            system.update(self.state, campaign_delta)
        return campaign_delta

    def set_time_scale(self, time_scale: int) -> None:
        """Change the campaign time multiplier."""

        self.tick()
        self._validate_time_scale(time_scale)
        previous_scale = self.time_scale
        self.time_scale = time_scale
        if previous_scale != time_scale:
            self.state.record_event(
                EventType.TIME_SCALE_CHANGED,
                {"from": previous_scale, "to": time_scale},
            )

    def snapshot(self) -> RuntimeSnapshot:
        """Tick and return a serializable runtime snapshot."""

        self.tick()
        # Runtime owns clock advancement; snapshot builders own DTO shape.
        return build_runtime_snapshot(self)

    @staticmethod
    def _validate_time_scale(time_scale: int) -> None:
        if time_scale not in ALLOWED_TIME_SCALES:
            allowed = ", ".join(str(scale) for scale in ALLOWED_TIME_SCALES)
            raise InvalidTimeScaleError(f"Time scale must be one of: {allowed}.")

    def _next_campaign_delta(self) -> timedelta:
        # Run systems only on whole campaign steps, not every wall-clock tick.
        due_steps = self._pending_campaign_delta // self.step_size
        if due_steps <= 0:
            return timedelta()

        campaign_delta = self.step_size * due_steps
        self._pending_campaign_delta -= campaign_delta
        return campaign_delta
