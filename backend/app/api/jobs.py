"""API routes for Job execution monitoring and Log inspection."""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.models.domain import Job, LogEntry
from app.services.repository import ops_repository

logger = logging.getLogger("app.api.jobs")
router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("", response_model=List[Job])
async def list_jobs(
    integration_id: Optional[str] = Query(None, description="Filter by integration ID"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status (SUCCESS | FAILED | RUNNING)"),
) -> List[Job]:
    """List synthetic data synchronization jobs with optional filtering."""
    logger.info("Listing jobs (integration_id=%s, status=%s)", integration_id, status_filter)
    return ops_repository.list_jobs(integration_id=integration_id, status=status_filter)


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str) -> Job:
    """Fetch details of a synthetic job execution by ID."""
    logger.info("Fetching job details: %s", job_id)
    job = ops_repository.get_job(job_id)
    if not job:
        logger.warning("Job not found: %s", job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    return job


@router.get("/{job_id}/logs", response_model=List[LogEntry])
async def get_job_logs(job_id: str) -> List[LogEntry]:
    """Fetch detailed log entries associated with a specific job ID."""
    logger.info("Fetching logs for job: %s", job_id)
    job = ops_repository.get_job(job_id)
    if not job:
        logger.warning("Job not found when requesting logs: %s", job_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found",
        )
    return ops_repository.get_job_logs(job_id)
