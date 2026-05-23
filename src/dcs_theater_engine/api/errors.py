"""Shared API error handling."""

from __future__ import annotations

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from dcs_theater_engine.campaign.errors import CampaignDomainError


def register_exception_handlers(app: FastAPI) -> None:
    """Register API-wide exception handlers."""

    # Convert expected campaign failures into one consistent HTTP response shape.
    @app.exception_handler(CampaignDomainError)
    async def campaign_domain_error_handler(
        _request: Request,
        exc: CampaignDomainError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": str(exc)},
        )

    # Convert request body/query validation failures in one shared place.
    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": jsonable_encoder(exc.errors())},
        )
