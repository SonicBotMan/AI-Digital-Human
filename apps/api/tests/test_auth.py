"""Tests for /api/auth endpoints — register, login, refresh, me."""

from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient

UNIQUE_EMAIL_PREFIX = "test_"


def _unique_email() -> str:
    return f"tester_{uuid.uuid4().hex[:8]}@example.com"


@pytest.mark.asyncio
async def test_register_new_user(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    response = await async_client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == email

    assert body["data"]["name"] == "Test User"


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    await async_client.post("/api/auth/register", json=payload)
    response = await async_client.post("/api/auth/register", json=payload)
    assert response.status_code == 409

    assert "already" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_returns_tokens(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    await async_client.post("/api/auth/register", json=payload)

    response = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": payload["password"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]
    assert body["data"]["token_type"] == "bearer"
    return body["data"]


@pytest.mark.asyncio
async def test_login_wrong_password_fails(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    await async_client.post("/api/auth/register", json=payload)

    response = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": "wrongpassword"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    await async_client.post("/api/auth/register", json=payload)
    login_resp = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": payload["password"]},
    )
    refresh_token = login_resp.json()["data"]["refresh_token"]

    response = await async_client.post(
        "/api/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]

    assert body["data"]["refresh_token"] != refresh_token


@pytest.mark.asyncio
async def test_refresh_token_reuse_fails(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    await async_client.post("/api/auth/register", json=payload)
    login_resp = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": payload["password"]},
    )
    refresh_token = login_resp.json()["data"]["refresh_token"]

    await async_client.post("/api/auth/refresh", json={"refresh_token": refresh_token})

    response = await async_client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_token(async_client: AsyncClient) -> None:
    email = _unique_email()
    payload = {"name": "Test User", "email": email, "password": "securepassword123"}
    await async_client.post("/api/auth/register", json=payload)
    login_resp = await async_client.post(
        "/api/auth/login",
        json={"email": email, "password": payload["password"]},
    )
    access_token = login_resp.json()["data"]["access_token"]

    response = await async_client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert body["data"]["email"] == email


@pytest.mark.asyncio
async def test_get_me_without_token_fails(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/auth/me")
    assert response.status_code in (401, 403)
