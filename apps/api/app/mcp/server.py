"""MCP Server implementation for AI Digital Human."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for MCP server."""
    logger.info("MCP Server starting up...")
    yield
    logger.info("MCP Server shutting down...")


def create_mcp_server() -> FastAPI:
    """Create and configure the MCP server FastAPI app."""
    mcp_app = FastAPI(
        title="AI Digital Human - MCP Server",
        version="1.0.0",
        docs_url="/mcp/docs",
        openapi_url="/mcp/openapi.json",
        lifespan=lifespan,
    )

    # Add CORS for MCP
    mcp_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Import and register tools
    from app.mcp.tools import get_mcp_tools

    tools = get_mcp_tools()

    @mcp_app.get("/tools")
    async def list_tools():
        """List all available MCP tools."""
        return {"tools": tools}

    @mcp_app.post("/tools/{tool_name}/call")
    async def call_tool(tool_name: str, params: dict):
        """Call an MCP tool with parameters."""
        from app.mcp.tools import chat_tool, memory_search_tool, face_lookup_tool

        tool_map = {
            "chat": chat_tool,
            "memory_search": memory_search_tool,
            "face_lookup": face_lookup_tool,
        }

        if tool_name not in tool_map:
            return {"error": f"Unknown tool: {tool_name}"}

        try:
            result = await tool_map[tool_name](**params)
            return {"success": True, "result": result}
        except Exception as e:
            logger.exception(f"Tool {tool_name} failed")
            return {"success": False, "error": "Tool execution failed"}

    @mcp_app.get("/health")
    async def health():
        """Health check for MCP server."""
        return {"status": "ok"}

    return mcp_app
