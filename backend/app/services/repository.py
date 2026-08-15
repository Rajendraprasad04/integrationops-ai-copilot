"""Synthetic Ops Repository service for reading integrations, jobs, and logs."""

import json
import logging
from pathlib import Path
from typing import List, Optional

from app.config import settings
from app.models.domain import Integration, Job, LogEntry

logger = logging.getLogger("app.services.repository")


class OpsRepository:
    """In-memory repository loading synthetic operational JSON data."""

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or settings.DATA_DIR)
        self._integrations: dict[str, Integration] = {}
        self._jobs: dict[str, Job] = {}
        self._logs: dict[str, List[LogEntry]] = {}
        self._loaded = False

    def load_data(self, force_reload: bool = False):
        """Load JSON synthetic datasets into memory."""
        if self._loaded and not force_reload:
            return

        # Load Integrations
        integrations_path = self.data_dir / "integrations.json"
        if integrations_path.exists():
            with open(integrations_path, "r", encoding="utf-8") as f:
                raw_integrations = json.load(f)
                self._integrations = {
                    item["integration_id"]: Integration(**item) for item in raw_integrations
                }
            logger.info("Loaded %d synthetic integrations", len(self._integrations))
        else:
            logger.warning("Integrations JSON file not found at %s", integrations_path)

        # Load Jobs
        jobs_path = self.data_dir / "jobs.json"
        if jobs_path.exists():
            with open(jobs_path, "r", encoding="utf-8") as f:
                raw_jobs = json.load(f)
                self._jobs = {item["job_id"]: Job(**item) for item in raw_jobs}
            logger.info("Loaded %d synthetic jobs", len(self._jobs))
        else:
            logger.warning("Jobs JSON file not found at %s", jobs_path)

        # Load Logs
        logs_path = self.data_dir / "logs.json"
        if logs_path.exists():
            with open(logs_path, "r", encoding="utf-8") as f:
                raw_logs = json.load(f)
                self._logs = {}
                for item in raw_logs:
                    log_entry = LogEntry(**item)
                    self._logs.setdefault(log_entry.job_id, []).append(log_entry)
            logger.info("Loaded logs for %d synthetic jobs", len(self._logs))
        else:
            logger.warning("Logs JSON file not found at %s", logs_path)

        self._loaded = True

    def get_integration(self, integration_id: str) -> Optional[Integration]:
        """Fetch a synthetic integration by ID."""
        self.load_data()
        return self._integrations.get(integration_id)

    def list_integrations(self) -> List[Integration]:
        """List all synthetic integrations."""
        self.load_data()
        return list(self._integrations.values())

    def get_job(self, job_id: str) -> Optional[Job]:
        """Fetch a synthetic job by ID."""
        self.load_data()
        return self._jobs.get(job_id)

    def list_jobs(
        self, integration_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[Job]:
        """List synthetic jobs with optional filtering by integration or status."""
        self.load_data()
        jobs = list(self._jobs.values())
        if integration_id:
            jobs = [j for j in jobs if j.integration == integration_id]
        if status:
            jobs = [j for j in jobs if j.status.upper() == status.upper()]
        return jobs

    def get_job_logs(self, job_id: str) -> List[LogEntry]:
        """Fetch synthetic logs associated with a job ID."""
        self.load_data()
        return self._logs.get(job_id, [])


# Global Repository Singleton instance
ops_repository = OpsRepository()
