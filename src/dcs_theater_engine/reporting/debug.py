"""Small debug helpers for early development."""

from dcs_theater_engine.campaign.core import CampaignState


def summarize_campaign(state: CampaignState) -> str:
    """Return a compact human-readable campaign summary."""

    return (
        f"{state.name}: {len(state.airbase_items())} airbases, "
        f"{len(state.squadron_items())} squadrons, {len(state.events)} events"
    )
