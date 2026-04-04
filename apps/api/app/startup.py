"""Startup seed logic for default data.

This module automatically seeds the database with default system prompts
and speaking styles on first startup, ensuring the system works
out-of-the-box without manual configuration.
"""

import logging

from sqlalchemy import select

from app.data.presets import DEFAULT_SYSTEM_PROMPTS, DEFAULT_SPEAKING_STYLES
from app.db.session import AsyncSessionLocal, init_db
from app.models.database import SystemPrompt, SpeakingStyle

logger = logging.getLogger(__name__)


async def seed_default_data() -> None:
    """Seed default system prompts and speaking styles if they don't exist."""
    async with AsyncSessionLocal() as db:
        # Check if we already have prompts
        result = await db.execute(select(SystemPrompt).limit(1))
        existing_prompts = result.scalars().first()

        if existing_prompts is None:
            logger.info("Seeding default system prompts...")
            for prompt_data in DEFAULT_SYSTEM_PROMPTS:
                prompt = SystemPrompt(
                    name=prompt_data["name"],
                    content=prompt_data["content"],
                    is_default=prompt_data["is_default"],
                )
                db.add(prompt)
            await db.commit()
            logger.info(f"Seeded {len(DEFAULT_SYSTEM_PROMPTS)} system prompts")
        else:
            logger.debug("System prompts already exist, skipping seed")

        # Check if we already have speaking styles
        result = await db.execute(select(SpeakingStyle).limit(1))
        existing_styles = result.scalars().first()

        if existing_styles is None:
            logger.info("Seeding default speaking styles...")
            for style_data in DEFAULT_SPEAKING_STYLES:
                style = SpeakingStyle(
                    name=style_data["name"],
                    description=style_data["description"],
                    style_config=style_data["style_config"],
                    is_default=style_data["is_default"],
                )
                db.add(style)
            await db.commit()
            logger.info(f"Seeded {len(DEFAULT_SPEAKING_STYLES)} speaking styles")
        else:
            logger.debug("Speaking styles already exist, skipping seed")


async def init_on_startup() -> None:
    """Called on application startup to initialize default data."""
    _warn_insecure_defaults()
    try:
        await init_db()
    except Exception:
        logger.exception("Failed to create database tables, continuing anyway")
    try:
        await seed_default_data()
    except Exception:
        logger.exception("Failed to seed default data, continuing anyway")


def _warn_insecure_defaults() -> None:
    from app.core.config import settings

    warnings: list[str] = []

    if settings.SECRET_KEY == "dev-secret-key-change-in-production":
        warnings.append("SECRET_KEY is using the default development value — change in production!")

    if settings.ADMIN_PASSWORD == "change-me-in-production":
        warnings.append("ADMIN_PASSWORD is using the default value — change in production!")

    if settings.DATABASE_URL.startswith("postgresql+asyncpg://postgres:postgres@localhost"):
        warnings.append("DATABASE_URL is using default PostgreSQL credentials — configure for production!")

    for warning in warnings:
        logger.warning("⚠️  SECURITY WARNING: %s", warning)
