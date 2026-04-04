"""Service registry for MCP tools.

The MCP server is a mounted FastAPI sub-app without access to the main app's
dependency injection. This module provides a thread-safe registry that is
populated during main app startup.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.services.chat_service import ChatService
    from app.services.face_service import FaceService
    from app.services.llm_service import LLMService
    from app.services.memory_service import MemoryService


@dataclass
class MCPToolServices:
    chat_service: ChatService
    llm_service: LLMService
    memory_service: MemoryService
    face_service: FaceService


_mcp_services: MCPToolServices | None = None


def register_mcp_services(services: MCPToolServices) -> None:
    global _mcp_services
    _mcp_services = services


def get_mcp_services() -> MCPToolServices:
    if _mcp_services is None:
        raise RuntimeError("MCP services not initialized")
    return _mcp_services
