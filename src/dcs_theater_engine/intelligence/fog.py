"""Coalition-specific known information."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from dcs_theater_engine.campaign.entities import Coalition


@dataclass(frozen=True, slots=True)
class ContactReport:
    """What one coalition believes about an entity."""

    entity_id: str
    coalition: Coalition
    last_seen_at: datetime
    confidence: float
    latitude: float | None = None
    longitude: float | None = None


@dataclass(slots=True)
class IntelligencePicture:
    """Known contacts for a coalition."""

    coalition: Coalition
    contacts: dict[str, ContactReport] = field(default_factory=dict)

    def update_contact(self, report: ContactReport) -> None:
        """Store or replace a contact report."""

        self.contacts[report.entity_id] = report
