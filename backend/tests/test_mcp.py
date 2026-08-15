"""Tests for minimal JSON-RPC 2.0 MCP server."""

from app.mcp_server import handle_mcp_request


def test_mcp_initialize():
    """Verify MCP initialize method response structure."""
    req = {"jsonrpc": "2.0", "id": 1, "method": "initialize"}
    resp = handle_mcp_request(req)
    assert resp["id"] == 1
    assert "result" in resp
    assert resp["result"]["serverInfo"]["name"] == "integrationops-mcp-server"


def test_mcp_tools_list():
    """Verify MCP tools/list returns get_job_status and get_job_logs schemas."""
    req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list"}
    resp = handle_mcp_request(req)
    assert resp["id"] == 2
    tools = resp["result"]["tools"]
    tool_names = [t["name"] for t in tools]
    assert "get_job_status" in tool_names
    assert "get_job_logs" in tool_names


def test_mcp_tools_call_job_status():
    """Verify MCP tools/call executes get_job_status for JOB-1001."""
    req = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_job_status",
            "arguments": {"job_id": "JOB-1001"},
        },
    }
    resp = handle_mcp_request(req)
    assert resp["id"] == 3
    content = resp["result"]["content"][0]["text"]
    assert "JOB-1001" in content
    assert "FAILED" in content
    assert "Publisher" in content


def test_mcp_tools_call_job_logs():
    """Verify MCP tools/call executes get_job_logs for JOB-1001."""
    req = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_job_logs",
            "arguments": {"job_id": "JOB-1001"},
        },
    }
    resp = handle_mcp_request(req)
    assert resp["id"] == 4
    content = resp["result"]["content"][0]["text"]
    assert "LOG-1001-01" in content
    assert "IngestEngine" in content


def test_mcp_unknown_tool():
    """Verify MCP handles unknown tool calls gracefully with JSON-RPC error."""
    req = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {"name": "unknown_tool", "arguments": {}},
    }
    resp = handle_mcp_request(req)
    assert "error" in resp
    assert resp["error"]["code"] == -32601
