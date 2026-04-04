import os
import re
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

from app.core.config import settings
from app.dependencies import AdminAuthDep

router = APIRouter(tags=["settings"])


class SettingsUpdate(BaseModel):
    LLM_PROVIDER: Optional[str] = None
    GLM_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    MINIMAX_API_KEY: Optional[str] = None


def mask_key(key: str) -> str:
    """Return a masked version of the API key for secure display."""
    if not key or len(key) < 8:
        return ""
    return key[:3] + "********" + key[-3:]


def update_env_file(key: str, value: str):
    """Write through configuration values into local .env file"""
    env_path = "../../.env" if not os.path.exists(".env") else ".env"

    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = rf"^{key}=.*$"
    if re.search(pattern, content, flags=re.MULTILINE):
        content = re.sub(pattern, f"{key}={value}", content, flags=re.MULTILINE)
    else:
        content += f"\n{key}={value}\n"

    with open(env_path, "w", encoding="utf-8") as f:
        f.write(content)


@router.get("/settings")
async def get_settings(_admin: AdminAuthDep):
    return {
        "LLM_PROVIDER": settings.LLM_PROVIDER,
        "GLM_API_KEY": mask_key(settings.GLM_API_KEY),
        "OPENAI_API_KEY": mask_key(settings.OPENAI_API_KEY),
        "MINIMAX_API_KEY": mask_key(settings.MINIMAX_API_KEY),
    }


@router.put("/settings")
async def update_settings(_admin: AdminAuthDep, payload: SettingsUpdate):
    if payload.LLM_PROVIDER:
        settings.LLM_PROVIDER = payload.LLM_PROVIDER
        update_env_file("LLM_PROVIDER", payload.LLM_PROVIDER)

    for field in ["GLM_API_KEY", "OPENAI_API_KEY", "MINIMAX_API_KEY"]:
        val = getattr(payload, field)
        # Avoid overriding with the masked string back to the config
        if val and "*" not in val:
            setattr(settings, field, val)
            update_env_file(field, val)

    return {"status": "success"}
