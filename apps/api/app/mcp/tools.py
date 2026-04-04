"""Custom MCP tools for the AI Digital Human system."""

from typing import Any

from app.mcp.registry import get_mcp_services


async def chat_tool(message: str, conversation_id: str | None = None, user_id: str = "default") -> dict[str, Any]:
    services = get_mcp_services()
    result = await services.chat_service.chat(
        user_id=user_id,
        message=message,
        conversation_id=conversation_id,
    )
    return {
        "reply": result.get("response", ""),
        "conversation_id": result.get("conversation_id", ""),
    }


async def memory_search_tool(query: str, user_id: str = "default", limit: int = 5) -> dict[str, Any]:
    services = get_mcp_services()
    embedding = services.llm_service.embed_text(query)
    memories = services.memory_service.search_memories(
        user_id=user_id,
        query_embedding=embedding,
        limit=limit,
    )
    return {
        "memories": memories,
        "count": len(memories),
    }


async def face_lookup_tool(image_data: str, top_k: int = 1) -> dict[str, Any]:
    services = get_mcp_services()
    embedding = services.face_service.extract_embedding(image_data)
    hit = services.memory_service.search_face(embedding=embedding)
    if hit is None:
        return {"matches": []}
    return {
        "matches": [
            {
                "name": hit.get("name", "unknown"),
                "user_id": hit.get("user_id", ""),
                "confidence": hit.get("score", 0.0),
            }
        ]
    }


def get_mcp_tools() -> list[dict[str, Any]]:
    """Return list of available MCP tools with their schemas."""
    return [
        {
            "name": "chat",
            "description": "Send a message to the AI digital human and get a response",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "The user's message"},
                    "conversation_id": {"type": "string", "description": "Optional conversation ID"},
                },
                "required": ["message"],
            },
        },
        {
            "name": "memory_search",
            "description": "Search the user's conversation memories",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "user_id": {"type": "string", "description": "User ID", "default": "default"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5},
                },
                "required": ["query"],
            },
        },
        {
            "name": "face_lookup",
            "description": "Identify a person from a face image",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "image_data": {"type": "string", "description": "Base64 image or URL"},
                    "top_k": {"type": "integer", "description": "Top K matches", "default": 1},
                },
                "required": ["image_data"],
            },
        },
    ]
