"""Tests for /api/settings endpoints — admin auth gating and CRUD."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_settings_without_auth_fails(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/settings")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_settings_with_admin_auth(async_client: AsyncClient, admin_headers: dict[str, str]) -> None:
    response = await async_client.get("/api/settings", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert "LLM_PROVIDER" in body


@pytest.mark.asyncio
async def test_update_settings_without_auth_fails(async_client: AsyncClient) -> None:
    response = await async_client.put(
        "/api/settings",
        json={"LLM_PROVIDER": "openai"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_settings_with_admin_auth(async_client: AsyncClient, admin_headers: dict[str, str]) -> None:
    response = await async_client.put(
        "/api/settings",
        json={"LLM_PROVIDER": "glm"},
        headers=admin_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
