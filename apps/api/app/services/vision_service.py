from __future__ import annotations

import base64
import io
import json
import logging
from pathlib import Path

from openai import AsyncOpenAI
from PIL import Image

from app.core.config import Settings

logger = logging.getLogger(__name__)

MAX_IMAGE_DIMENSION = 2048
SUPPORTED_FORMATS = {"PNG", "JPEG", "WEBP"}
DEFAULT_ANALYSIS_PROMPT = (
    "Analyze this image in detail. Provide a JSON response with these fields:\n"
    '"description": "A detailed visual description of the image",\n'
    '"expressions": "List of detected emotions or expressions, or empty list if none",\n'
    '"scene_info": {"context": "Scene context", "objects": ["list of detected objects"]},\n'
    '"people": [{"description": "Person description", "attributes": "Visible attributes"}] or empty list\n'
    "Respond with valid JSON only."
)

FRAME_ANALYSIS_PROMPT = (
    "Analyze these video frames in sequence. Provide a JSON response with:\n"
    '"description": "Description of the sequence of events across frames",\n'
    '"expressions": "List of emotions or expressions detected across frames",\n'
    '"scene_info": {"context": "Scene context", "objects": ["objects detected"], "activity": "Activity described across frames"},\n'
    '"people": [{"description": "Person description", "attributes": "Visible attributes"}] or empty list\n'
    "Respond with valid JSON only."
)


def _encode_image(image_path: str | Path) -> tuple[str, str]:
    """Load image, resize if needed, return (base64_data, mime_type)."""
    path = Path(image_path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")

    img = Image.open(path)
    fmt = img.format
    if fmt is None:
        suffix = path.suffix.lower()
        fmt = {"png": "PNG", "jpg": "JPEG", "jpeg": "JPEG", "webp": "WEBP"}.get(suffix.lstrip("."), "JPEG")

    if fmt.upper() not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported image format: {fmt}. Supported: {SUPPORTED_FORMATS}")

    if max(img.size) > MAX_IMAGE_DIMENSION:
        img.thumbnail((MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION), Image.Resampling.LANCZOS)

    if img.mode == "RGBA" and fmt.upper() == "JPEG":
        img = img.convert("RGB")

    buffer = io.BytesIO()
    img.save(buffer, format=fmt)
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    mime_map = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}
    return b64, mime_map.get(fmt.upper(), "image/jpeg")


def _build_image_content(b64: str, mime: str) -> dict:
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def _parse_response(raw: str) -> dict:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "description": raw,
            "expressions": [],
            "scene_info": {"context": "", "objects": []},
            "people": [],
        }


class VisionService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._model = settings.VISION_MODEL
        self._max_tokens = settings.VISION_MAX_TOKENS
        self._provider = settings.VISION_PROVIDER

        if self._provider == "glm":
            from zhipuai import ZhipuAI

            self._client = ZhipuAI(api_key=settings.GLM_API_KEY)
        elif self._provider == "minimax":
            self._client = None
        else:
            self._client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def _call_vision(self, image_contents: list[dict], prompt: str) -> dict:
        if self._provider == "glm":
            return await self._call_glm_vision(image_contents, prompt)
        elif self._provider == "minimax":
            return await self._call_minimax_vision(image_contents, prompt)
        else:
            messages = [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}, *image_contents],
                }
            ]
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=messages,
                max_tokens=self._max_tokens,
            )
            raw = response.choices[0].message.content or ""
            return _parse_response(raw)

    async def _call_glm_vision(self, image_contents: list[dict], prompt: str) -> dict:
        messages = [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}, *image_contents],
            }
        ]
        response = self._client.chat.completions.create(
            model=self._model,
            messages=messages,
            max_tokens=self._max_tokens,
        )
        raw = response.choices[0].message.content or ""
        return _parse_response(raw)

    async def _call_minimax_vision(self, image_contents: list[dict], prompt: str) -> dict:
        import httpx

        url = f"https://api.minimax.chat/v1/multimodal/chat/completions?GroupId={self._settings.MINIMAX_GROUP_ID}"
        headers = {"Authorization": f"Bearer {self._settings.MINIMAX_API_KEY}"}
        payload = {
            "model": "MiniMax-VL-01",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}, *image_contents],
                }
            ],
            "max_tokens": self._max_tokens,
        }
        resp = httpx.post(url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        raw = resp.json()["choices"][0]["message"]["content"]
        return _parse_response(raw)

    async def analyze_image(self, image_path: str | Path, prompt: str | None = None) -> dict:
        b64, mime = _encode_image(image_path)
        content = _build_image_content(b64, mime)
        analysis_prompt = prompt or DEFAULT_ANALYSIS_PROMPT
        return await self._call_vision([content], analysis_prompt)

    async def analyze_images(self, image_paths: list[str | Path], prompt: str | None = None) -> dict:
        if not image_paths:
            raise ValueError("At least one image path is required")

        contents: list[dict] = []
        for path in image_paths:
            b64, mime = _encode_image(path)
            contents.append(_build_image_content(b64, mime))

        analysis_prompt = prompt or DEFAULT_ANALYSIS_PROMPT
        return await self._call_vision(contents, analysis_prompt)

    async def analyze_video_frames(self, frame_paths: list[str | Path], prompt: str | None = None) -> dict:
        if not frame_paths:
            raise ValueError("At least one frame path is required")

        contents: list[dict] = []
        for path in frame_paths:
            b64, mime = _encode_image(path)
            contents.append(_build_image_content(b64, mime))

        analysis_prompt = prompt or FRAME_ANALYSIS_PROMPT
        return await self._call_vision(contents, analysis_prompt)
