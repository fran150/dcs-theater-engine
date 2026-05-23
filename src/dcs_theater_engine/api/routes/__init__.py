"""Route registry for the FastAPI application."""

# Import each route module so the app can register them in one place.
from dcs_theater_engine.api.routes import campaign, health, theaters, ui

# Keep route registration order explicit and easy to extend.
ROUTERS = (
    health.router,
    ui.router,
    theaters.router,
    campaign.router,
)

# Expose only the route registry to the application factory.
__all__ = ["ROUTERS"]
