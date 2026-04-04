"""Multimodal analysis router — multi-modal input processing."""

from __future__ import annotations

import base64
import logging
from typing import Any, Optional

from fastapi import APIRouter, File, Form, UploadFile

from app.dependencies import (
    FaceServiceDep,
    MemoryServiceDep,
    SettingsDep,
    STTServiceDep,
    UserAuthDep,
    VisionServiceDep,
)
from app.models.schemas import MultimodalAnalysisResult, StandardResponse
from app.services.multimodal_service import MultimodalService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analyze", tags=["multimodal"])


def _build_multimodal_service(
    settings: Any,
    face: Any,
    stt: Any,
    vision: Any,
    memory: Any,
) -> MultimodalService:
    return MultimodalService(
        settings=settings,
        face_service=face,
        stt_service=stt,
        vision_service=vision,
        memory_service=memory,
    )


async def _file_to_data_uri(upload: UploadFile) -> str | None:
    if not upload or not upload.filename:
        return None
    content = await upload.read()
    mime = upload.content_type or "application/octet-stream"
    b64 = base64.b64encode(content).decode()
    return f"data:{mime};base64,{b64}"


@router.post(
    "",
    response_model=StandardResponse[MultimodalAnalysisResult],
)
async def analyze(
    current_user: UserAuthDep,
    settings: SettingsDep,
    face: FaceServiceDep,
    stt: STTServiceDep,
    vision: VisionServiceDep,
    memory: MemoryServiceDep,
    text: Optional[str] = Form(default=None),
    images: list[UploadFile] = File(default=[]),
    audio: Optional[UploadFile] = File(default=None),
    video: Optional[UploadFile] = File(default=None),
    context: Optional[str] = Form(default=None),
) -> StandardResponse[MultimodalAnalysisResult]:
    """Accept multipart/form-data with text, images, audio, and/or video and return unified analysis."""
    service = _build_multimodal_service(settings, face, stt, vision, memory)

    image_uris: list[str] = []
    for img in images:
        uri = await _file_to_data_uri(img)
        if uri:
            image_uris.append(uri)

    audio_uri = await _file_to_data_uri(audio) if audio else None
    video_uri = await _file_to_data_uri(video) if video else None

    raw = await service.process_input(
        text=text,
        images=image_uris or None,
        audio=audio_uri,
        video=video_uri,
        context=context,
    )

    result = MultimodalAnalysisResult(
        transcript=raw.get("audio_transcript", {}).get("text") if raw.get("audio_transcript") else None,
        description=(raw["visual_analysis"][0].get("description") if raw.get("visual_analysis") else None),
        summary=raw.get("text_content", "") or raw.get("context", "") or "No content provided",
        detected_objects=_extract_detected_objects(raw),
        sentiment=None,
        confidence=raw.get("metadata", {}).get("confidence", 0.0),
    )

    return StandardResponse(
        success=True,
        message="Analysis completed",
        data=result,
    )


def _extract_detected_objects(raw: dict[str, Any]) -> list[str]:
    objects: list[str] = []
    for analysis in raw.get("visual_analysis", []):
        if isinstance(analysis, dict):
            detected = analysis.get("detected_objects", [])
            if isinstance(detected, list):
                objects.extend(detected)
    return objects
