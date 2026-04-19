"""Application entrypoint for the MCP Email Service."""

from fastapi import FastAPI

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:  # pragma: no cover - optional runtime dependency
    FastMCP = None  # type: ignore[assignment]


app = FastAPI(title="MCP Email Service")

if FastMCP is not None:
    mcp = FastMCP("email-service", transport="streamable-http")
    app.mount("/mcp", mcp.streamable_http_app())
else:
    mcp = None
