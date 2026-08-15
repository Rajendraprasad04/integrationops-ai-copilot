"""Minimal, zero-dependency Model Context Protocol (MCP) stdio server.

Exposes IntegrationOps operational tools to any MCP Client (e.g. Claude Desktop, Cursor, Antigravity)
via standard JSON-RPC 2.0 over stdio transport.
"""

import sys
import json
import logging
from typing import Any, Dict

from app.agent.tools import (
    get_job_status,
    get_job_logs,
    get_integration_config,
    get_pipeline_metrics,
)

logger = logging.getLogger("mcp_server")


def handle_mcp_request(request: Dict[str, Any]) -> Dict[str, Any]:
    """Process incoming JSON-RPC 2.0 MCP request."""
    req_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {
                    "name": "integrationops-mcp-server",
                    "version": "0.1.0",
                },
            },
        }

    elif method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "get_job_status",
                        "description": "Fetch status, failing service, error message, and record counts for an integration job ID.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "job_id": {"type": "string", "description": "Job ID (e.g. JOB-1001)"}
                            },
                            "required": ["job_id"],
                        },
                    },
                    {
                        "name": "get_job_logs",
                        "description": "Fetch detailed stack trace and execution logs for a job ID.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "job_id": {"type": "string", "description": "Job ID (e.g. JOB-1001)"}
                            },
                            "required": ["job_id"],
                        },
                    },
                ]
            },
        }

    elif method == "tools/call":
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        job_id = arguments.get("job_id", "")

        if tool_name == "get_job_status":
            result = get_job_status(job_id)
        elif tool_name == "get_job_logs":
            result = get_job_logs(job_id)
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"},
            }

        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2),
                    }
                ]
            },
        }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not supported"},
    }


def main():
    """Run line-delimited JSON-RPC stdio message loop."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_mcp_request(request)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
        except Exception as e:
            err_resp = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
            }
            sys.stdout.write(json.dumps(err_resp) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
