# AI Agent Architecture & Tool Calling Specification

## Overview
The **IntegrationOps AI Copilot** uses a **Simple Single-Agent Architecture** to assist operations engineers in diagnosing pipeline failures, checking job execution metrics, and retrieving standard operating procedures.

Unlike passive documentation search engines, the agent combines **real-time tool calling** (to inspect live job state and error logs) with **RAG document search** (to retrieve troubleshooting manuals).

---

## The Single-Agent Lifecycle (Agent Loop)

```
[ User Question ] ("Why did JOB-1001 fail and what should normally happen during publishing?")
       │
       ▼
 1. [ Decision ] ──► Detects entities ("JOB-1001", "publishing") & determines required tools/docs
       │
       ▼
 2. [ Action ] ──► Executes get_job_status("JOB-1001"), get_job_logs("JOB-1001"), and RAG doc search
       │
       ▼
 3. [ Observation ] ──► Collects structured tool JSON outputs + document context snippets
       │
       ▼
 4. [ Final Response ] ──► Synthesizes grounded answer containing failure diagnosis & standard procedures
```

---

## Core Agent Concepts

### 1. Agent
An autonomous software wrapper that evaluates user intent, decides necessary actions, calls external functions or retrieval modules, gathers observations, and generates a grounded response.

### 2. Tool
A strongly typed, independently testable Python function (e.g., `get_job_status`, `get_job_logs`, `get_pipeline_metrics`, `get_integration_config`) that accepts validated input parameters and returns structured operational JSON data.

### 3. Decision
The routing stage where the agent analyzes the question to determine whether to execute operational tools, search documentation, or both. In IntegrationOps AI Copilot, entity extraction (`JOB-1001`) and keyword intent matching drive deterministic, reliable tool selection.

### 4. Action
The physical invocation of selected tools (e.g., calling `get_job_status("JOB-1001")`) or running vector similarity search against the document index.

### 5. Observation
The concrete outputs resulting from actions. Observations include status dictionaries, stack trace logs, and retrieved Markdown chunks.

### 6. Final Response
The final synthesized natural language answer presented to the user, complete with source document citations (`sources`) and a record of invoked functions (`tools_used`).

---

## RAG vs. Tool Calling

| Dimension | Retrieval-Augmented Generation (RAG) | Operational Tool Calling |
|---|---|---|
| **Data Source** | Unstructured Markdown manuals (`data/docs/*.md`). | Structured operational datasets (`jobs.json`, `logs.json`). |
| **Information Type** | Static rules, SLA policies, standard operating procedures. | Dynamic real-time system state (job status, record counts, stack traces). |
| **Invocation Trigger** | Conceptual queries ("What is the publishing flow?"). | Entity-specific queries ("What happened to JOB-1001?"). |
| **Output Structure** | Text chunks + metadata (`document_name`, `section`). | Structured JSON objects (`status`, `records_failed`, `error_message`). |

---

## RAG + Agent Synergies

By integrating RAG with tool calling, the copilot resolves complex operational scenarios that neither technology can solve alone:

* **Example Hybrid Query**: *"Why did JOB-1001 fail and what should normally happen during publishing?"*
  1. **Tool Execution (Agent)**: Calls `get_job_status("JOB-1001")` and `get_job_logs("JOB-1001")` ➔ Discovers `EX_SCHEMA_VALIDATION_ERROR` on column `customer_email` (length 82 vs VARCHAR(50)).
  2. **Document Retrieval (RAG)**: Retrieves `publishing.md` ➔ Finds standard pre-publish validation rules and batch upsert specifications.
  3. **Synthesis**: Synthesizes a unified response explaining *what actually failed in JOB-1001* alongside *how publishing is supposed to function*.
