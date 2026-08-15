"""Deterministic Tool Router and Orchestration Engine."""

import re
import logging
from typing import Any, Dict, List, Tuple

from app.agent.tools import (
    get_integration_config,
    get_job_logs,
    get_job_status,
    get_pipeline_metrics,
)

logger = logging.getLogger("app.agent.orchestrator")

JOB_PATTERN = re.compile(r"\b(JOB-\d+)\b", re.IGNORECASE)

KNOWN_INTEGRATIONS = [
    "salesforce_postgres",
    "github_bigquery",
    "servicenow_postgres",
    "stripe_kafka",
    "datadog_postgres",
]


class AgentOrchestrator:
    """Orchestrates intent detection, entity extraction, and deterministic tool execution."""

    def analyze_and_execute_tools(self, question: str) -> Tuple[List[str], List[str]]:
        """Detect entities in question, run appropriate tools, and return (tools_used, formatted_contexts)."""
        question_upper = question.upper()
        question_lower = question.lower()
        tools_used: List[str] = []
        tool_contexts: List[str] = []

        # 1. Detect Job IDs
        job_matches = JOB_PATTERN.findall(question)

        for job_id in set(job_matches):
            clean_job_id = job_id.upper()

            # Decide which job tools to run based on question keywords
            is_metrics_query = any(k in question_lower for k in ["metrics", "record", "failed", "how many", "count"])
            is_status_log_query = any(k in question_lower for k in ["status", "happened", "why", "fail", "log", "error"]) or not is_metrics_query

            if is_status_log_query:
                # Run get_job_status
                tools_used.append("get_job_status")
                status_res = get_job_status(clean_job_id)
                tool_contexts.append(f"[Tool Output: get_job_status({clean_job_id})]\n{status_res}")

                # Run get_job_logs if checking failures or what happened
                tools_used.append("get_job_logs")
                logs_res = get_job_logs(clean_job_id)
                tool_contexts.append(f"[Tool Output: get_job_logs({clean_job_id})]\n{logs_res}")

            if is_metrics_query and "get_job_status" not in tools_used:
                tools_used.append("get_pipeline_metrics")
                metrics_res = get_pipeline_metrics(clean_job_id)
                tool_contexts.append(f"[Tool Output: get_pipeline_metrics({clean_job_id})]\n{metrics_res}")

        # 2. Detect Integration IDs
        for integ in KNOWN_INTEGRATIONS:
            if integ in question_lower:
                tools_used.append("get_integration_config")
                config_res = get_integration_config(integ)
                tool_contexts.append(f"[Tool Output: get_integration_config({integ})]\n{config_res}")

        # Deduplicate tools_used preserving order
        unique_tools = []
        for t in tools_used:
            if t not in unique_tools:
                unique_tools.append(t)

        logger.info("Question '%s' triggered tools: %s", question, unique_tools)
        return unique_tools, tool_contexts


# Global Agent Orchestrator Singleton
agent_orchestrator = AgentOrchestrator()
