"""System status and health check routes."""

import logging
from fastapi import APIRouter
from app.config import settings
from app.models.schemas import HealthResponse, SystemInfoResponse

logger = logging.getLogger("app.api.health")
router = APIRouter(tags=["System"])


@router.get("/", response_model=SystemInfoResponse)
async def get_root() -> SystemInfoResponse:
    """Root endpoint returning service identity and documentation location."""
    logger.info("Root endpoint accessed")
    return SystemInfoResponse(
        message="Welcome to IntegrationOps AI Copilot API",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        docs_url="/docs",
    )


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Health check endpoint for monitoring service availability."""
    logger.info("Health check endpoint queried")
    return HealthResponse(
        status="ok",
        service=settings.SERVICE_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
    )
