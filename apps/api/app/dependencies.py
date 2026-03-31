"""FastAPI dependency providers for services and database access."""

import os
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends

from app.core.config import Settings, settings
from app.db.session import get_db


# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------


@lru_cache
def get_settings() -> Settings:
    return settings


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

get_db = get_db  # noqa: F811

DbSession = Annotated[Any, Depends(get_db)]


# ---------------------------------------------------------------------------
# Service providers
# ---------------------------------------------------------------------------

_TEST_MODE = os.getenv("APP_TEST_MODE", "").lower() in ("1", "true", "yes")


def _mock_service(name: str) -> Any:
    """Return a lightweight mock that records calls (for tests)."""
    from unittest.mock import AsyncMock

    return AsyncMock(name=name)


@lru_cache
def _get_llm_service() -> Any:
    if _TEST_MODE:
        return _mock_service("LLMService")
    from app.services.llm import LLMService  # type: ignore[import-untyped]

    return LLMService(settings)


@lru_cache
def _get_face_service() -> Any:
    if _TEST_MODE:
        return _mock_service("FaceService")
    from app.services.face import FaceService  # type: ignore[import-untyped]

    return FaceService(settings)


@lru_cache
def _get_stt_service() -> Any:
    if _TEST_MODE:
        return _mock_service("STTService")
    from app.services.stt import STTService  # type: ignore[import-untyped]

    return STTService(settings)


@lru_cache
def _get_vision_service() -> Any:
    if _TEST_MODE:
        return _mock_service("VisionService")
    from app.services.vision import VisionService  # type: ignore[import-untyped]

    return VisionService(settings)


@lru_cache
def _get_memory_service() -> Any:
    if _TEST_MODE:
        return _mock_service("MemoryService")
    from app.services.memory import MemoryService  # type: ignore[import-untyped]

    return MemoryService(settings)


@lru_cache
def _get_graph_service() -> Any:
    if _TEST_MODE:
        return _mock_service("GraphService")
    from app.services.graph import GraphService  # type: ignore[import-untyped]

    return GraphService(settings)


@lru_cache
def _get_chat_service() -> Any:
    if _TEST_MODE:
        return _mock_service("ChatService")
    from app.services.chat import ChatService  # type: ignore[import-untyped]

    return ChatService(settings)


# Public async wrappers (FastAPI supports async generators & async callables)


async def get_llm_service() -> Any:
    return _get_llm_service()


async def get_face_service() -> Any:
    return _get_face_service()


async def get_stt_service() -> Any:
    return _get_stt_service()


async def get_vision_service() -> Any:
    return _get_vision_service()


async def get_memory_service() -> Any:
    return _get_memory_service()


async def get_graph_service() -> Any:
    return _get_graph_service()


async def get_chat_service() -> Any:
    return _get_chat_service()


# Annotated aliases for concise injection in route handlers

LLMServiceDep = Annotated[Any, Depends(get_llm_service)]
FaceServiceDep = Annotated[Any, Depends(get_face_service)]
STTServiceDep = Annotated[Any, Depends(get_stt_service)]
VisionServiceDep = Annotated[Any, Depends(get_vision_service)]
MemoryServiceDep = Annotated[Any, Depends(get_memory_service)]
GraphServiceDep = Annotated[Any, Depends(get_graph_service)]
ChatServiceDep = Annotated[Any, Depends(get_chat_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]
