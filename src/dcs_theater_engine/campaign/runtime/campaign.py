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

# Systems advance in fixed campaign-time chunks. At higher time scales, tick()
# runs more chunks per real second instead of making each chunk larger.
# The default step is one campaign second, so at 64x the runtime processes
# 64 one-second campaign steps for every real second.
DEFAULT_CAMPAIGN_STEP = timedelta(seconds=1)


@dataclass(slots=True)
class CampaignRuntime:
    """Coordinates campaign time and coarse runtime systems.

    CampaignRuntime converts elapsed wall-clock time into campaign-time steps,
    advances the authoritative campaign state, and runs each configured system
    once for every complete campaign step that is due.

    Attributes:
        state: Authoritative mutable campaign state advanced by the runtime.
        systems: Campaign systems updated after each completed campaign step.
        time_scale: Multiplier applied to elapsed wall-clock time.
        running: Whether wall-clock time should currently advance the campaign.
        clock: Callable that returns the current real UTC time. Injectable for tests.
        step_size: Minimum campaign-time chunk processed per update.
    """

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
        self._validate_step_size(self.step_size)
        self._last_real_tick = self.clock()

    def tick(self) -> timedelta:
        """Advance campaign time when enough paced time has accumulated."""

        # Calculate how much real time has passed since the last tick.
        current_real_time = self.clock()
        real_delta = current_real_time - self._last_real_tick
        self._last_real_tick = current_real_time

        if not self.running or real_delta.total_seconds() <= 0:
            return timedelta()

        # Convert real elapsed time into campaign time and keep fractional
        # leftovers until enough campaign time exists for another fixed step.
        self._pending_campaign_delta += real_delta * self.time_scale
        total_campaign_delta = timedelta()
        while self._pending_campaign_delta >= self.step_size:
            # Process one fixed campaign step at a time so fast-forward runs
            # more updates instead of giving systems a larger variable delta.
            self._pending_campaign_delta -= self.step_size

            # Update campaign time and trigger updates in all systems.
            self.state.current_time += self.step_size
            for system in self.systems:
                system.update(self.state, self.step_size)

            # Accumulate total campaign delta for callers that need a summary.
            total_campaign_delta += self.step_size

        return total_campaign_delta

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
        """Return a serializable runtime snapshot without advancing time."""

        # Runtime owns campaign state; snapshot builders own DTO shape.
        return build_runtime_snapshot(self)

    @staticmethod
    def _validate_time_scale(time_scale: int) -> None:
        if time_scale not in ALLOWED_TIME_SCALES:
            allowed = ", ".join(str(scale) for scale in ALLOWED_TIME_SCALES)
            raise InvalidTimeScaleError(f"Time scale must be one of: {allowed}.")

    @staticmethod
    def _validate_step_size(step_size: timedelta) -> None:
        if step_size <= timedelta():
            raise ValueError("Campaign step size must be positive.")
