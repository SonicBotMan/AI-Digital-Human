"""Tests for /api/chat endpoints — send message, list conversations, history, WebSocket stream."""

from __future__ import annotations

from collections.abc import AsyncGenerator
import uuid
from unittest.mock import AsyncMock

import pytest
from httpx import AsyncClient

from app.dependencies import get_chat_service
from app.main import app

REGISTER_PAYLOAD = {
    "name": "Chat Tester",
    "email": "chattester@example.com",
    "password": "securepassword123",
}


async def _register_and_login(async_client: AsyncClient) -> dict[str, str]:
    await async_client.post("/api/auth/register", json=REGISTER_PAYLOAD)
    login_resp = await async_client.post(
        "/api/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    tokens = login_resp.json()["data"]
    return {"Authorization": f"Bearer {tokens['access_token']}"}


async def _mock_chat_service(
    return_value: dict,
) -> None:
    mock_svc = AsyncMock(name="ChatService")
    conv_id = str(uuid.uuid4())
    mock_svc.chat.return_value = {
        "response": "Hello! How can I help?",
        "conversation_id": conv_id,
        "message_id": str(uuid.uuid4()),
        "entities_extracted": [],
    }

    app.dependency_overrides[get_chat_service] = _override_get_chat_service(mock_svc)
    return mock_svc


async def _cleanup_chat_override() -> None:
    app.dependency_overrides.pop(get_chat_service, None)


@pytest.mark.asyncio
async def test_send_message(async_client: AsyncClient) -> None:
    headers = await _register_and_login(async_client)
    mock_svc = await _mock_chat_service()

    response = await async_client.post(
        "/api/chat",
        json={"message": "Hello!"},
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "message" in body["data"]
    assert "conversation_id" in body["data"]
    await _cleanup_chat_override()


@pytest.mark.asyncio
async def test_send_message_unauthenticated(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/chat",
        json={"message": "Hello!"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_list_conversations(async_client: AsyncClient) -> None:
    headers = await _register_and_login(async_client)
    mock_svc = AsyncMock(name="ChatService")
    mock_svc.list_conversations.return_value = ([], 0)
    app.dependency_overrides[get_chat_service] = _override_get_chat_service(mock_svc)

    response = await async_client.get(
        "/api/chat/conversations",
        headers=headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    await _cleanup_chat_override()


@pytest.mark.asyncio
async def test_get_conversation_history(async_client: AsyncClient) -> None:
    headers = await _register_and_login(async_client)
    conv_id = str(uuid.uuid4())
    mock_svc = AsyncMock(name="ChatService")
    mock_svc.get_conversation_history.return_value = []
    app.dependency_overrides[get_chat_service] = _override_get_chat_service(mock_svc)
    response = await async_client.get(
        f"/api/chat/conversations/{conv_id}",
        headers=headers,
    )
    assert response.status_code in (200, 403)
    await _cleanup_chat_override()


@pytest.mark.asyncio
async def test_websocket_stream(async_client: AsyncClient) -> None:
    headers = await _register_and_login(async_client)
    bearer_token = headers["Authorization"].replace("Bearer ", "")
    mock_svc = AsyncMock(name="ChatService")

    async def _fake_stream(*args, **kwargs):
        yield {"type": "token", "content": "Hi"}
        yield {"type": "end", "conversation_id": str(uuid.uuid4()), "message_id": str(uuid.uuid4())}

    mock_svc.stream_chat = _fake_stream
    app.dependency_overrides[get_chat_service] = _override_get_chat_service(mock_svc)

    async with async_client.websocket_connect(f"/api/chat/stream?token={bearer_token}") as ws:
        ws.send_json({"content": "Hello", "conversation_id": None})
        start_msg = ws.receive_json()
        assert start_msg["type"] == "start"
        token_msg = ws.receive_json()
        assert token_msg["type"] == "token"
        end_msg = ws.receive_json()
        assert end_msg["type"] == "end"

    await _cleanup_chat_override()
