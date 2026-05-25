"""Thread-safe access to a campaign runtime."""

from __future__ import annotations

from datetime import timedelta
from threading import RLock

from dcs_theater_engine.campaign.runtime.campaign import CampaignRuntime
from dcs_theater_engine.campaign.runtime.snapshots import RuntimeSnapshot


class CampaignRuntimeService:
    """Synchronizes runtime ticks, commands, and snapshots.

    The API may read snapshots while the app-owned runtime loop is advancing
    campaign state. This service keeps those operations from interleaving.

    Attributes:
        runtime: Mutable campaign runtime protected by this service.
    """

    def __init__(self, runtime: CampaignRuntime) -> None:
        self.runtime = runtime
        self._lock = RLock()

    def tick(self) -> timedelta:
        """Advance the runtime under the service lock."""

        with self._lock:
            return self.runtime.tick()

    def set_time_scale(self, time_scale: int) -> None:
        """Change the runtime speed under the service lock."""

        with self._lock:
            self.runtime.set_time_scale(time_scale)

    def snapshot(self) -> RuntimeSnapshot:
        """Read the current runtime snapshot under the service lock."""

        with self._lock:
            return self.runtime.snapshot()
