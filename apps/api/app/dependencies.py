"""FastAPI dependency providers for services and database access."""

import os
from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends
from fastapi.security import HTTPBasic, HTTPBasicCredentials, HTTPAuthorizationCredentials, HTTPBearer

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
# User Auth (JWT Bearer)
# ---------------------------------------------------------------------------

_bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
    db: Any = Depends(get_db),
) -> Any:
    """Extract and verify JWT from Authorization header, return the User ORM object."""
    from fastapi import HTTPException, status
    from jose import JWTError

    from app.core.security import verify_access_token
    from app.models.database import User

    try:
        user_id = verify_access_token(credentials.credentials)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


UserAuthDep = Annotated[Any, Depends(get_current_user)]


# ---------------------------------------------------------------------------
# Service providers
# ---------------------------------------------------------------------------

_TEST_MODE = os.getenv("APP_TEST_MODE", "").lower() in ("1", "true", "yes")


def _mock_service(name: str) -> Any:
    """Return a lightweight mock that records calls (for tests)."""
    from unittest.mock import AsyncMock

    return AsyncMock(name=name)


async def _get_llm_service(db: DbSession) -> Any:
    if _TEST_MODE:
        return _mock_service("LLMService")
    from app.services.llm_service import LLMService  # type: ignore[import-untyped]
    from app.models.database import ModelConfig
    from sqlalchemy import select

    # Fetch active config from DB to get vendor overrides
    result = await db.execute(select(ModelConfig).where(ModelConfig.is_active == True).limit(1))
    config = result.scalars().first()
    vendor_configs = config.vendor_configs if config else None

    return LLMService(settings, vendor_configs=vendor_configs)


def _get_face_service() -> Any:
    if _TEST_MODE:
        return _mock_service("FaceService")
    from app.services.face_service import FaceService  # type: ignore[import-untyped]

    return FaceService(settings)


def _get_stt_service() -> Any:
    if _TEST_MODE:
        return _mock_service("STTService")
    from app.services.stt_service import STTService  # type: ignore[import-untyped]

    return STTService(settings)


def _get_vision_service() -> Any:
    if _TEST_MODE:
        return _mock_service("VisionService")
    from app.services.vision_service import VisionService  # type: ignore[import-untyped]

    return VisionService(settings)


def _get_memory_service() -> Any:
    if _TEST_MODE:
        return _mock_service("MemoryService")
    from app.services.memory_service import MemoryService  # type: ignore[import-untyped]

    return MemoryService(settings)


def _get_graph_service(db: DbSession) -> Any:
    if _TEST_MODE:
        return _mock_service("GraphService")
    from app.services.graph_service import GraphService  # type: ignore[import-untyped]

    return GraphService(db)


async def get_chat_service(db: DbSession) -> Any:
    if _TEST_MODE:
        return _mock_service("ChatService")
    from app.services.chat_service import ChatService  # type: ignore[import-untyped]

    llm = await _get_llm_service(db)
    memory = _get_memory_service()
    graph = _get_graph_service(db)

    return ChatService(
        db_session=db,
        llm_service=llm,
        memory_service=memory,
        graph_service=graph,
        settings=settings,
    )


# Public async wrappers (FastAPI supports async generators & async callables)


async def get_llm_service(db: DbSession) -> Any:
    return await _get_llm_service(db)


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


# Annotated aliases for concise injection in route handlers

LLMServiceDep = Annotated[Any, Depends(get_llm_service)]
FaceServiceDep = Annotated[Any, Depends(get_face_service)]
STTServiceDep = Annotated[Any, Depends(get_stt_service)]
VisionServiceDep = Annotated[Any, Depends(get_vision_service)]
MemoryServiceDep = Annotated[Any, Depends(get_memory_service)]
GraphServiceDep = Annotated[Any, Depends(get_graph_service)]
ChatServiceDep = Annotated[Any, Depends(get_chat_service)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


# ---------------------------------------------------------------------------
# Admin Auth (HTTP Basic)
# ---------------------------------------------------------------------------


async def get_admin_auth(
    credentials: HTTPBasicCredentials = Depends(HTTPBasic(auto_error=False)),
    db: Any = Depends(get_db),
) -> None:
    from fastapi import HTTPException, status
    from sqlalchemy import select

    from app.core.security import verify_password
    from app.models.database import AdminProfile

    # 1. Get current hash from DB (if exists) or use config default
    result = await db.execute(select(AdminProfile).limit(1))
    profile = result.scalars().first()

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Admin credentials required",
        )

    if profile:
        # Use DB hash
        is_valid = verify_password(credentials.password, profile.password_hash)
        # Note: We currently hardcode admin username check too if needed
        # but the primary check is credentials matched provided
        is_valid = is_valid and (credentials.username == settings.ADMIN_USERNAME)
    else:
        # Fallback to config default
        is_valid = credentials.username == settings.ADMIN_USERNAME and credentials.password == settings.ADMIN_PASSWORD

    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            # We omit "WWW-Authenticate" to prevent the browser from showing its native login dialog
        )


AdminAuthDep = Annotated[None, Depends(get_admin_auth)]
