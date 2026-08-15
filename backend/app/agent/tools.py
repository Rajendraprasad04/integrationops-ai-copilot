"""Operational tools for inspecting synthetic integrations, jobs, logs, and metrics."""

import logging
from typing import Any, Dict
from app.services.repository import ops_repository

logger = logging.getLogger("app.agent.tools")


def get_job_status(job_id: str) -> Dict[str, Any]:
    """Retrieve operational status, metadata, and error message for a job ID."""
    if not job_id or not isinstance(job_id, str):
        return {"error": "Invalid job_id provided", "status": "INVALID_INPUT"}

    clean_id = job_id.strip().upper()
    job = ops_repository.get_job(clean_id)
    if not job:
        return {"error": f"Job '{clean_id}' not found", "found": False}

    return {
        "found": True,
        "job_id": job.job_id,
        "integration": job.integration,
        "status": job.status,
        "service": job.service,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
        "records_processed": job.records_processed,
        "records_failed": job.records_failed,
        "error_message": job.error_message,
    }


def get_job_logs(job_id: str) -> Dict[str, Any]:
    """Retrieve log trace entries associated with a job ID."""
    if not job_id or not isinstance(job_id, str):
        return {"error": "Invalid job_id provided", "status": "INVALID_INPUT"}

    clean_id = job_id.strip().upper()
    job = ops_repository.get_job(clean_id)
    if not job:
        return {"error": f"Job '{clean_id}' not found", "found": False, "logs": []}

    logs = ops_repository.get_job_logs(clean_id)
    log_entries = [
        {
            "log_id": log.log_id,
            "timestamp": log.timestamp,
            "level": log.level,
            "service": log.service,
            "message": log.message,
        }
        for log in logs
    ]

    return {
        "found": True,
        "job_id": clean_id,
        "log_count": len(log_entries),
        "logs": log_entries,
    }


def get_integration_config(integration_id: str) -> Dict[str, Any]:
    """Retrieve configuration metadata for an integration flow by ID."""
    if not integration_id or not isinstance(integration_id, str):
        return {"error": "Invalid integration_id provided", "status": "INVALID_INPUT"}

    clean_id = integration_id.strip().lower()
    integration = ops_repository.get_integration(clean_id)
    if not integration:
        return {"error": f"Integration '{clean_id}' not found", "found": False}

    return {
        "found": True,
        "integration_id": integration.integration_id,
        "name": integration.name,
        "source_system": integration.source_system,
        "destination_system": integration.destination_system,
        "schedule": integration.schedule,
        "status": integration.status,
        "owner_email": integration.owner_email,
        "created_at": integration.created_at,
    }


def get_pipeline_metrics(job_id: str) -> Dict[str, Any]:
    """Calculate pipeline throughput, failure rates, and execution metrics for a job ID."""
    if not job_id or not isinstance(job_id, str):
        return {"error": "Invalid job_id provided", "status": "INVALID_INPUT"}

    clean_id = job_id.strip().upper()
    job = ops_repository.get_job(clean_id)
    if not job:
        return {"error": f"Job '{clean_id}' not found", "found": False}

    total_records = job.records_processed + job.records_failed
    failure_rate = (
        round((job.records_failed / total_records) * 100.0, 2)
        if total_records > 0
        else 0.0
    )

    return {
        "found": True,
        "job_id": job.job_id,
        "integration": job.integration,
        "records_processed": job.records_processed,
        "records_failed": job.records_failed,
        "total_records_handled": total_records,
        "failure_rate_percent": failure_rate,
        "service": job.service,
        "status": job.status,
    }
