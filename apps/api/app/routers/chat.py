"""Chat router — conversation management and streaming responses."""

from __future__ import annotations

import json
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.dependencies import ChatServiceDep
from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationListResponse,
    ConversationMessage,
    StandardResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# ---------------------------------------------------------------------------
# REST endpoints
# ---------------------------------------------------------------------------


@router.post("", response_model=StandardResponse[ChatResponse])
async def send_message(
    body: ChatRequest,
    service: ChatServiceDep,
) -> StandardResponse[ChatResponse]:
    """Send a message to the AI digital human and receive a response."""
    result = await service.send_message(
        message=body.message,
        conversation_id=body.conversation_id,
        images=body.images,
        system_prompt_id=body.system_prompt_id,
    )
    return StandardResponse(
        success=True,
        message="Message sent successfully",
        data=ChatResponse(**result),
    )


@router.get(
    "/conversations",
    response_model=StandardResponse[list[ConversationListResponse]],
)
async def list_conversations(
    service: ChatServiceDep,
    *,
    page: int = 1,
    page_size: int = 20,
) -> StandardResponse[list[ConversationListResponse]]:
    """List all conversations for the current user."""
    result = await service.list_conversations(page=page, page_size=page_size)
    return StandardResponse(
        success=True,
        message="Conversations retrieved",
        data=[ConversationListResponse(**c) for c in result],
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=StandardResponse[list[ConversationMessage]],
)
async def get_conversation(
    conversation_id: UUID,
    service: ChatServiceDep,
) -> StandardResponse[list[ConversationMessage]]:
    """Retrieve the full message history of a conversation."""
    result = await service.get_conversation(conversation_id=conversation_id)
    return StandardResponse(
        success=True,
        message="Conversation retrieved",
        data=[ConversationMessage(**m) for m in result],
    )


@router.delete(
    "/conversations/{conversation_id}",
    response_model=StandardResponse[None],
)
async def delete_conversation(
    conversation_id: UUID,
    service: ChatServiceDep,
) -> StandardResponse[None]:
    """Delete a conversation and all its messages."""
    await service.delete_conversation(conversation_id=conversation_id)
    return StandardResponse(
        success=True,
        message="Conversation deleted",
    )


# ---------------------------------------------------------------------------
# WebSocket streaming
# ---------------------------------------------------------------------------


class _StreamMessage(BaseModel):
    """Incoming WebSocket message schema for streaming chat."""

    message: str = Field(min_length=1, description="User text message")
    conversation_id: UUID | None = Field(
        default=None,
        description="Continue an existing conversation",
    )
    system_prompt_id: UUID | None = Field(
        default=None,
        description="Override system prompt",
    )


@router.websocket("/stream")
async def stream_chat(
    websocket: WebSocket,
    service: ChatServiceDep,
) -> None:
    """WebSocket endpoint for streaming chat responses.

    Protocol
    --------
    Client sends JSON::

        {"message": "Hello", "conversation_id": null}

    Server streams back JSON chunks::

        {"type": "chunk",  "content": "Hello"}
        {"type": "done",   "conversation_id": "...", "message": "..."}
        {"type": "error",  "detail": "..."}

    The connection stays open for multiple round-trips until the client
    disconnects.
    """
    await websocket.accept()

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                payload = _StreamMessage.model_validate_json(raw)
            except Exception as exc:
                await websocket.send_json({"type": "error", "detail": f"Invalid message: {exc}"})
                continue

            try:
                async for chunk in service.stream_message(
                    message=payload.message,
                    conversation_id=payload.conversation_id,
                    system_prompt_id=payload.system_prompt_id,
                ):
                    chunk_type = chunk.get("type", "chunk")

                    if chunk_type == "done":
                        await websocket.send_json(
                            {
                                "type": "done",
                                "conversation_id": str(chunk.get("conversation_id", "")),
                                "message": chunk.get("message", ""),
                            }
                        )
                    else:
                        await websocket.send_json(
                            {
                                "type": "chunk",
                                "content": chunk.get("content", ""),
                            }
                        )

            except Exception as exc:
                logger.exception("Streaming error")
                await websocket.send_json({"type": "error", "detail": str(exc)})

    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected")
