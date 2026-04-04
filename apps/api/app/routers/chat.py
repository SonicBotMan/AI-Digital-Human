"""Chat router — conversation management and streaming responses."""

from __future__ import annotations

import json
import logging
import uuid as _uuid
from uuid import UUID

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, status
from jose import JWTError
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select

from app.core.security import verify_access_token
from app.dependencies import ChatServiceDep, DbSession, UserAuthDep
from app.models.database import Conversation
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
    current_user: UserAuthDep,
) -> StandardResponse[ChatResponse]:
    """Send a message to the AI digital human and receive a response."""
    result = await service.chat(
        user_id=current_user.id,
        message=body.message,
        conversation_id=body.conversation_id,
    )
    return StandardResponse(
        success=True,
        message="Message sent successfully",
        data=ChatResponse(
            message=result["response"],
            conversation_id=result["conversation_id"],
        ),
    )


@router.get(
    "/conversations",
    response_model=StandardResponse[list[ConversationListResponse]],
)
async def list_conversations(
    service: ChatServiceDep,
    current_user: UserAuthDep,
    *,
    page: int = 1,
    page_size: int = 20,
) -> StandardResponse[list[ConversationListResponse]]:
    """List all conversations for the current user."""
    items, total = await service.list_conversations(
        user_id=str(current_user.id),
        page=page,
        page_size=page_size,
    )
    return StandardResponse(
        success=True,
        message=f"Conversations retrieved (total: {total})",
        data=items,
    )


async def _verify_conversation_ownership(
    db: DbSession,
    conversation_id: UUID,
    current_user: UserAuthDep,
) -> None:
    """Verify that *conversation_id* belongs to *current_user*.

    Raises ``HTTPException(403)`` if the conversation does not exist or
    belongs to a different user.
    """
    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conversation not found or access denied",
        )


@router.get(
    "/conversations/{conversation_id}",
    response_model=StandardResponse[list[ConversationMessage]],
)
async def get_conversation(
    conversation_id: UUID,
    service: ChatServiceDep,
    current_user: UserAuthDep,
    db: DbSession,
) -> StandardResponse[list[ConversationMessage]]:
    """Retrieve the full message history of a conversation."""
    await _verify_conversation_ownership(db, conversation_id, current_user)
    result = await service.get_conversation_history(conversation_id=conversation_id)
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
    current_user: UserAuthDep,
    db: DbSession,
) -> StandardResponse[None]:
    """Delete a conversation and all its messages."""
    await _verify_conversation_ownership(db, conversation_id, current_user)

    stmt = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()
    if conversation:
        await db.delete(conversation)
        await db.commit()

    return StandardResponse(
        success=True,
        message="Conversation deleted",
    )


# ---------------------------------------------------------------------------
# WebSocket streaming
# ---------------------------------------------------------------------------


class _StreamMessage(BaseModel):
    """Incoming WebSocket message schema for streaming chat.

    Accepts both {"message": "..."} and {"content": "..."} formats
    to maintain compatibility with the frontend protocol.
    """

    model_config = ConfigDict(populate_by_name=True)

    message: str = Field(min_length=1, alias="content", description="User text message")
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

    Authentication
    --------------
    The client must include a valid JWT access token either:

    1. Via the ``token`` query parameter: ``ws://…/stream?token=<jwt>``
    2. Via the ``Authorization`` header in the handshake
       (``Authorization: Bearer <jwt>``)

    If the token is missing or invalid the connection is closed with
    code 4001 (custom close code meaning "unauthenticated").

    Protocol
    --------
    Client sends JSON::

        {"content": "Hello", "conversation_id": null}

    Server streams back JSON events::

        {"type": "start",  "id": "uuid"}
        {"type": "token",  "content": "Hel"}
        {"type": "token",  "content": "lo"}
        ...
        {"type": "end",    "conversation_id": "...", "message_id": "..."}
        {"type": "error",  "detail": "..."}

    The connection stays open for multiple round-trips until the client
    disconnects.
    """
    # --- Authenticate the WebSocket handshake ---
    token: str | None = websocket.query_params.get("token")
    if not token:
        auth_header = websocket.headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()

    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    try:
        user_id = verify_access_token(token)
    except JWTError:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

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
                msg_id = str(_uuid.uuid4())
                await websocket.send_json({"type": "start", "id": msg_id})

                async for event in service.stream_chat(
                    user_id=user_id,
                    message=payload.message,
                    conversation_id=payload.conversation_id,
                ):
                    await websocket.send_json(event)

            except Exception as exc:
                logger.exception("Chat error")
                await websocket.send_json({"type": "error", "detail": "Server error occurred"})

    except WebSocketDisconnect:
        logger.debug("WebSocket client disconnected")
