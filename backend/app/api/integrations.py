"""API routes for Integrations management."""

import logging
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.domain import Integration
from app.services.repository import ops_repository

logger = logging.getLogger("app.api.integrations")
router = APIRouter(prefix="/integrations", tags=["Integrations"])


@router.get("", response_model=List[Integration])
async def list_integrations() -> List[Integration]:
    """List all synthetic integration pipelines."""
    logger.info("Listing all synthetic integrations")
    return ops_repository.list_integrations()


@router.get("/{integration_id}", response_model=Integration)
async def get_integration(integration_id: str) -> Integration:
    """Fetch details of a synthetic integration pipeline by ID."""
    logger.info("Fetching integration: %s", integration_id)
    integration = ops_repository.get_integration(integration_id)
    if not integration:
        logger.warning("Integration not found: %s", integration_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Integration '{integration_id}' not found",
        )
    return integration
