"""Domain Pydantic schemas for Integrations, Jobs, and Logs."""

from typing import Optional
from pydantic import BaseModel, Field


class Integration(BaseModel):
    """Integration data flow configuration domain model."""

    integration_id: str = Field(..., description="Unique integration identifier")
    name: str = Field(..., description="Human-readable integration name")
    source_system: str = Field(..., description="Source system name")
    destination_system: str = Field(..., description="Destination system name")
    schedule: str = Field(..., description="Cron schedule or execution frequency")
    status: str = Field(..., description="Current status (HEALTHY | DEGRADED | FAILED)")
    owner_email: str = Field(..., description="Owner contact email")
    created_at: str = Field(..., description="ISO 8601 creation timestamp")


class Job(BaseModel):
    """Data synchronization job execution record domain model."""

    job_id: str = Field(..., description="Unique job execution identifier")
    integration: str = Field(..., description="Associated integration ID")
    status: str = Field(..., description="Execution status (SUCCESS | FAILED | RUNNING)")
    started_at: str = Field(..., description="ISO 8601 start timestamp")
    completed_at: Optional[str] = Field(None, description="ISO 8601 completion timestamp")
    records_processed: int = Field(default=0, description="Total records processed")
    records_failed: int = Field(default=0, description="Number of failed records")
    service: str = Field(..., description="Service component responsible for execution")
    error_message: Optional[str] = Field(None, description="Error message if job failed")


class LogEntry(BaseModel):
    """Individual log event entry associated with a job execution."""

    log_id: str = Field(..., description="Unique log entry identifier")
    job_id: str = Field(..., description="Associated job ID")
    timestamp: str = Field(..., description="ISO 8601 log timestamp")
    level: str = Field(..., description="Log severity level (INFO | WARN | ERROR)")
    service: str = Field(..., description="Service component emitting the log")
    message: str = Field(..., description="Detailed log message")
