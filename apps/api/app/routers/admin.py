"""Admin settings router – CRUD for system prompts, speaking styles, and model configs."""

import uuid

from fastapi import APIRouter, HTTPException
from sqlalchemy import select

from app.dependencies import DbSession
from app.models.database import ModelConfig, SpeakingStyle, SystemPrompt
from app.models.schemas import (
    ModelConfigResponse,
    ModelConfigUpdate,
    SpeakingStyleCreate,
    SpeakingStyleResponse,
    SpeakingStyleUpdate,
    StandardResponse,
    SystemPromptCreate,
    SystemPromptResponse,
    SystemPromptUpdate,
)

router = APIRouter(prefix="/admin", tags=["admin"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _prompt_not_found(prompt_id: uuid.UUID) -> HTTPException:
    return HTTPException(status_code=404, detail=f"System prompt {prompt_id} not found")


def _style_not_found(style_id: uuid.UUID) -> HTTPException:
    return HTTPException(status_code=404, detail=f"Speaking style {style_id} not found")


# ---------------------------------------------------------------------------
# System Prompts
# ---------------------------------------------------------------------------


@router.get("/prompts", response_model=StandardResponse[list[SystemPromptResponse]])
async def list_prompts(db: DbSession) -> StandardResponse[list[SystemPromptResponse]]:
    result = await db.execute(select(SystemPrompt).order_by(SystemPrompt.created_at.desc()))
    prompts = result.scalars().all()
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(prompts)} system prompt(s)",
        data=[SystemPromptResponse.model_validate(p) for p in prompts],
    )


@router.post("/prompts", response_model=StandardResponse[SystemPromptResponse], status_code=201)
async def create_prompt(
    body: SystemPromptCreate,
    db: DbSession,
) -> StandardResponse[SystemPromptResponse]:
    if body.is_default:
        existing = (await db.execute(select(SystemPrompt).where(SystemPrompt.is_default.is_(True)))).scalars().all()
        for p in existing:
            p.is_default = False

    prompt = SystemPrompt(
        name=body.name,
        content=body.content,
        is_default=body.is_default,
    )
    db.add(prompt)
    await db.flush()
    await db.refresh(prompt)
    return StandardResponse(
        success=True,
        message="System prompt created",
        data=SystemPromptResponse.model_validate(prompt),
    )


@router.get("/prompts/{prompt_id}", response_model=StandardResponse[SystemPromptResponse])
async def get_prompt(
    prompt_id: uuid.UUID,
    db: DbSession,
) -> StandardResponse[SystemPromptResponse]:
    prompt = await db.get(SystemPrompt, prompt_id)
    if not prompt:
        raise _prompt_not_found(prompt_id)
    return StandardResponse(
        success=True,
        message="System prompt retrieved",
        data=SystemPromptResponse.model_validate(prompt),
    )


@router.put("/prompts/{prompt_id}", response_model=StandardResponse[SystemPromptResponse])
async def update_prompt(
    prompt_id: uuid.UUID,
    body: SystemPromptUpdate,
    db: DbSession,
) -> StandardResponse[SystemPromptResponse]:
    prompt = await db.get(SystemPrompt, prompt_id)
    if not prompt:
        raise _prompt_not_found(prompt_id)

    update_data = body.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        existing = (await db.execute(select(SystemPrompt).where(SystemPrompt.is_default.is_(True)))).scalars().all()
        for p in existing:
            if p.id != prompt_id:
                p.is_default = False

    for field, value in update_data.items():
        setattr(prompt, field, value)

    await db.flush()
    await db.refresh(prompt)
    return StandardResponse(
        success=True,
        message="System prompt updated",
        data=SystemPromptResponse.model_validate(prompt),
    )


@router.delete("/prompts/{prompt_id}", response_model=StandardResponse[None])
async def delete_prompt(
    prompt_id: uuid.UUID,
    db: DbSession,
) -> StandardResponse[None]:
    prompt = await db.get(SystemPrompt, prompt_id)
    if not prompt:
        raise _prompt_not_found(prompt_id)
    await db.delete(prompt)
    await db.flush()
    return StandardResponse(success=True, message="System prompt deleted", data=None)


@router.post(
    "/prompts/{prompt_id}/set-default",
    response_model=StandardResponse[SystemPromptResponse],
)
async def set_default_prompt(
    prompt_id: uuid.UUID,
    db: DbSession,
) -> StandardResponse[SystemPromptResponse]:
    prompt = await db.get(SystemPrompt, prompt_id)
    if not prompt:
        raise _prompt_not_found(prompt_id)

    existing = (await db.execute(select(SystemPrompt).where(SystemPrompt.is_default.is_(True)))).scalars().all()
    for p in existing:
        p.is_default = False

    prompt.is_default = True
    await db.flush()
    await db.refresh(prompt)
    return StandardResponse(
        success=True,
        message=f"System prompt '{prompt.name}' set as default",
        data=SystemPromptResponse.model_validate(prompt),
    )


# ---------------------------------------------------------------------------
# Speaking Styles
# ---------------------------------------------------------------------------


@router.get("/styles", response_model=StandardResponse[list[SpeakingStyleResponse]])
async def list_styles(db: DbSession) -> StandardResponse[list[SpeakingStyleResponse]]:
    result = await db.execute(select(SpeakingStyle).order_by(SpeakingStyle.created_at.desc()))
    styles = result.scalars().all()
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(styles)} speaking style(s)",
        data=[SpeakingStyleResponse.model_validate(s) for s in styles],
    )


@router.post("/styles", response_model=StandardResponse[SpeakingStyleResponse], status_code=201)
async def create_style(
    body: SpeakingStyleCreate,
    db: DbSession,
) -> StandardResponse[SpeakingStyleResponse]:
    if body.is_default:
        existing = (await db.execute(select(SpeakingStyle).where(SpeakingStyle.is_default.is_(True)))).scalars().all()
        for s in existing:
            s.is_default = False

    style = SpeakingStyle(
        name=body.name,
        description=body.description,
        style_config=body.style_config,
        is_default=body.is_default,
    )
    db.add(style)
    await db.flush()
    await db.refresh(style)
    return StandardResponse(
        success=True,
        message="Speaking style created",
        data=SpeakingStyleResponse.model_validate(style),
    )


@router.get("/styles/{style_id}", response_model=StandardResponse[SpeakingStyleResponse])
async def get_style(
    style_id: uuid.UUID,
    db: DbSession,
) -> StandardResponse[SpeakingStyleResponse]:
    style = await db.get(SpeakingStyle, style_id)
    if not style:
        raise _style_not_found(style_id)
    return StandardResponse(
        success=True,
        message="Speaking style retrieved",
        data=SpeakingStyleResponse.model_validate(style),
    )


@router.put("/styles/{style_id}", response_model=StandardResponse[SpeakingStyleResponse])
async def update_style(
    style_id: uuid.UUID,
    body: SpeakingStyleUpdate,
    db: DbSession,
) -> StandardResponse[SpeakingStyleResponse]:
    style = await db.get(SpeakingStyle, style_id)
    if not style:
        raise _style_not_found(style_id)

    update_data = body.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        existing = (await db.execute(select(SpeakingStyle).where(SpeakingStyle.is_default.is_(True)))).scalars().all()
        for s in existing:
            if s.id != style_id:
                s.is_default = False

    for field, value in update_data.items():
        setattr(style, field, value)

    await db.flush()
    await db.refresh(style)
    return StandardResponse(
        success=True,
        message="Speaking style updated",
        data=SpeakingStyleResponse.model_validate(style),
    )


@router.delete("/styles/{style_id}", response_model=StandardResponse[None])
async def delete_style(
    style_id: uuid.UUID,
    db: DbSession,
) -> StandardResponse[None]:
    style = await db.get(SpeakingStyle, style_id)
    if not style:
        raise _style_not_found(style_id)
    await db.delete(style)
    await db.flush()
    return StandardResponse(success=True, message="Speaking style deleted", data=None)


# ---------------------------------------------------------------------------
# Model Configuration
# ---------------------------------------------------------------------------


@router.get("/models", response_model=StandardResponse[ModelConfigResponse])
async def get_model_config(db: DbSession) -> StandardResponse[ModelConfigResponse]:
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.is_active.is_(True)).order_by(ModelConfig.updated_at.desc())
    )
    config = result.scalars().first()

    if not config:
        config = ModelConfig(
            llm_model="openai:gpt-4o",
            vision_model="gpt-4o",
            stt_model="turbo",
            temperature=0.7,
            max_tokens=4096,
            is_active=True,
        )
        db.add(config)
        await db.flush()
        await db.refresh(config)

    return StandardResponse(
        success=True,
        message="Active model configuration retrieved",
        data=ModelConfigResponse.model_validate(config),
    )


@router.put("/models", response_model=StandardResponse[ModelConfigResponse])
async def update_model_config(
    body: ModelConfigUpdate,
    db: DbSession,
) -> StandardResponse[ModelConfigResponse]:
    result = await db.execute(
        select(ModelConfig).where(ModelConfig.is_active.is_(True)).order_by(ModelConfig.updated_at.desc())
    )
    config = result.scalars().first()

    if not config:
        config = ModelConfig(
            llm_model="openai:gpt-4o",
            vision_model="gpt-4o",
            stt_model="turbo",
            temperature=0.7,
            max_tokens=4096,
            is_active=True,
        )
        db.add(config)
        await db.flush()
        await db.refresh(config)

    update_data = body.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)

    await db.flush()
    await db.refresh(config)
    return StandardResponse(
        success=True,
        message="Model configuration updated",
        data=ModelConfigResponse.model_validate(config),
    )
