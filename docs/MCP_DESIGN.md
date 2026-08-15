# Model Context Protocol (MCP) Design & Implementation Specification

## Executive Overview
The **Model Context Protocol (MCP)** is an open standard developed to standardize how AI applications (clients) connect to external tools, databases, and context sources (servers).

In **IntegrationOps AI Copilot**, MCP allows external AI environments (such as Claude Desktop, Antigravity, or Cursor) to inspect operational job states (`get_job_status`), fetch error logs (`get_job_logs`), and query integration configurations without custom API integrations.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│              MCP Client (Host Environment)               │
│      (e.g., Claude Desktop, Antigravity IDE, Cursor)     │
└────────────────────────────┬─────────────────────────────┘
                             │
                             │ (JSON-RPC 2.0 over stdio / SSE)
                             ▼
┌──────────────────────────────────────────────────────────┐
│             IntegrationOps MCP Server                    │
│             (backend/app/mcp_server.py)                  │
├────────────────────────────┬─────────────────────────────┤
│  Exposed MCP Tools         │  Exposed MCP Resources      │
│  - get_job_status          │  - integrationops://jobs    │
│  - get_job_logs            │  - integrationops://docs    │
└──────────────┬─────────────┴──────────────┬──────────────┘
               │                            │
               ▼                            ▼
┌──────────────────────────────────────────────────────────┐
│                Synthetic Data Repository                 │
│         (backend/data/jobs.json, logs.json)              │
└──────────────────────────────────────────────────────────┘
```

---

## Core MCP Concepts

### 1. What MCP Is
MCP is an open client-server protocol (using JSON-RPC 2.0 specification) that defines how an AI application discovers capabilities, retrieves contextual resources, and executes external tools hosted on remote or local servers.

### 2. Why MCP Exists
Before MCP, every AI tool integration required custom glue code specific to each LLM vendor API (OpenAI function schemas vs Gemini tool signatures vs Anthropic tool definitions). MCP eliminates vendor lock-in: an engineer writes a single MCP server, and *any* MCP-compatible AI client can consume it natively.

### 3. MCP Client
The host software (e.g. Claude Desktop, Antigravity, Cursor) that initiates connection to an MCP server. The client reads available tools from the server, passes user queries to the LLM, and dispatches tool execution requests back to the MCP server.

### 4. MCP Server
A lightweight background process (connected via `stdio` pipe or HTTP `SSE`) that exposes tools, resources, and prompt templates to MCP clients.

### 5. Tools
Executable functions exposed by the MCP server that perform actions or state lookups. In IntegrationOps, `get_job_status` and `get_job_logs` are exposed as MCP tools with JSON Schema input parameters.

### 6. Resources
Read-only contextual data URIs exposed by an MCP server (such as `integrationops://integrations/salesforce_postgres` or `integrationops://docs/publishing.md`).

---

## MCP vs. Ordinary Function Calling

| Dimension | Ordinary LLM Function Calling | Model Context Protocol (MCP) |
|---|---|---|
| **Protocol Standard** | Vendor-specific (OpenAI JSON format, Gemini payload format). | Open Standard (JSON-RPC 2.0). |
| **Portability** | Tied to a specific LLM API provider SDK. | Universal: 1 server works across Claude, Cursor, Antigravity, etc. |
| **Transport** | Embedded inside LLM HTTP requests. | Standalone transport (`stdio` process pipes or HTTP SSE streams). |
| **Security & Governance** | Handled manually per API call. | Encapsulated within server process permissions and standard transport protocols. |

---

## Tool Mapping: IntegrationOps to MCP

Our synthetic operations tools map directly into standard MCP Tool Definitions:

### 1. `get_job_status`
- **MCP Tool Name**: `get_job_status`
- **Description**: Returns status, failing service, error message, and record counts for an integration job ID.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "job_id": { "type": "string", "description": "Job execution ID (e.g. JOB-1001)" }
    },
    "required": ["job_id"]
  }
  ```

### 2. `get_job_logs`
- **MCP Tool Name**: `get_job_logs`
- **Description**: Fetches detailed log traces (INFO, WARN, ERROR) associated with a job ID.
- **Input Schema**:
  ```json
  {
    "type": "object",
    "properties": {
      "job_id": { "type": "string", "description": "Job execution ID (e.g. JOB-1001)" }
    },
    "required": ["job_id"]
  }
  ```

---

## JSON-RPC 2.0 Stdio Execution Example

### Step 1: Client Initialize Request
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": { "name": "Antigravity", "version": "1.0.0" }
  }
}
```

### Step 2: Tool Call Request (`get_job_status`)
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "get_job_status",
    "arguments": { "job_id": "JOB-1001" }
  }
}
```

### Step 3: MCP Server Response
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\n  \"found\": true,\n  \"job_id\": \"JOB-1001\",\n  \"status\": \"FAILED\",\n  \"service\": \"Publisher\",\n  \"error_message\": \"Destination validation failed: target table schema mismatch on column 'customer_email'\"\n}"
      }
    ]
  }
}
```

---

## Running the Minimal MCP Stdio Server

The minimal zero-dependency stdio MCP server is implemented in [`backend/app/mcp_server.py`](file:///C:/Users/kraje/.gemini/antigravity-ide/scratch/integrationops-ai/backend/app/mcp_server.py).

To configure in Claude Desktop / Antigravity configuration file (`mcp_config.json`):
```json
{
  "mcpServers": {
    "integrationops": {
      "command": "python",
      "args": ["-m", "app.mcp_server"],
      "cwd": "C:/Users/kraje/.gemini/antigravity-ide/scratch/integrationops-ai/backend"
    }
  }
}
```
