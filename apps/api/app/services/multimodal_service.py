"""Multimodal orchestrator service for the AI Digital Human platform.

Coordinates FaceService, STTService, VisionService, and MemoryService
to process heterogeneous input (text, images, audio, video) into a
unified analysis result ready for ChatService consumption.
"""

from __future__ import annotations

import asyncio
import base64
import logging
import tempfile
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Coroutine, Protocol

from app.core.config import Settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Limits / defaults
# ---------------------------------------------------------------------------

MAX_VIDEO_FRAMES = 8
VIDEO_FRAME_INTERVAL_SEC = 1.0
SUPPORTED_IMAGE_EXTS = frozenset({".png", ".jpg", ".jpeg", ".webp", ".bmp"})
SUPPORTED_AUDIO_EXTS = frozenset({".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac"})
SUPPORTED_VIDEO_EXTS = frozenset({".mp4", ".avi", ".mov", ".mkv", ".webm"})


# ---------------------------------------------------------------------------
# Lightweight protocol definitions so the orchestrator does not import
# concrete service modules directly (keeps the layer clean).
# ---------------------------------------------------------------------------


class _FaceServiceProto(Protocol):
    def identify_face(
        self,
        image_input: str | Path,
        stored_embeddings: list[dict],
        threshold: float | None = None,
    ) -> dict | None: ...


class _STTServiceProto(Protocol):
    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> dict: ...

    def transcribe_audio_or_extract(
        self,
        media_path: str | Path,
        language: str | None = None,
    ) -> dict: ...


class _VisionServiceProto(Protocol):
    async def analyze_image(
        self,
        image_path: str | Path,
        prompt: str | None = None,
    ) -> dict: ...

    async def analyze_images(
        self,
        image_paths: list[str | Path],
        prompt: str | None = None,
    ) -> dict: ...

    async def analyze_video_frames(
        self,
        frame_paths: list[str | Path],
        prompt: str | None = None,
    ) -> dict: ...


class _MemoryServiceProto(Protocol):
    def get_all_face_embeddings(self) -> list[dict]: ...


# ---------------------------------------------------------------------------
# Helper data classes
# ---------------------------------------------------------------------------


@dataclass
class _ModalityError:
    modality: str
    error: str


@dataclass
class _ProcessingMetadata:
    request_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    started_at: float = field(default_factory=time.monotonic)
    finished_at: float = 0.0
    errors: list[_ModalityError] = field(default_factory=list)

    @property
    def elapsed_ms(self) -> float:
        end = self.finished_at or time.monotonic()
        return round((end - self.started_at) * 1000, 1)

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "elapsed_ms": self.elapsed_ms,
            "errors": [{"modality": e.modality, "error": e.error} for e in self.errors],
        }


# ---------------------------------------------------------------------------
# Video helpers (frame + audio extraction)
# ---------------------------------------------------------------------------


def _extract_video_frames(
    video_path: str | Path,
    interval: float = VIDEO_FRAME_INTERVAL_SEC,
    max_frames: int = MAX_VIDEO_FRAMES,
    output_dir: str | Path | None = None,
) -> list[Path]:
    """Extract evenly-spaced frames from a video file using OpenCV.

    Returns a list of temporary image file paths.
    """
    import cv2

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
    frame_interval = max(1, int(fps * interval))

    out_dir = Path(output_dir) if output_dir else Path(tempfile.mkdtemp(prefix="mm_frames_"))

    frames: list[Path] = []
    idx = 0
    saved = 0

    while saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % frame_interval == 0:
            frame_path = out_dir / f"frame_{saved:04d}.jpg"
            cv2.imwrite(str(frame_path), frame)
            frames.append(frame_path)
            saved += 1
        idx += 1

    cap.release()
    logger.debug("Extracted %d frames from %s (total=%d, fps=%.1f)", saved, video_path, total, fps)
    return frames


def _extract_audio_from_video(
    video_path: str | Path,
    output_path: str | Path | None = None,
) -> Path:
    """Extract the audio track from a video file via ffmpeg.

    Returns the path to a temporary WAV file.
    """
    import subprocess

    out = Path(output_path) if output_path else Path(tempfile.mktemp(suffix=".wav"))

    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(video_path),
            "-vn",
            "-ar",
            "16000",
            "-ac",
            "1",
            "-f",
            "wav",
            "-acodec",
            "pcm_s16le",
            "-hide_banner",
            "-loglevel",
            "error",
            str(out),
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffmpeg audio extraction failed (rc={result.returncode}): {result.stderr.decode(errors='replace')}"
        )
    return out


def _resolve_input_path(raw: str | Path) -> Path:
    """Resolve a string/Path input to a real filesystem Path.

    Supports file paths and ``data:`` base64 URIs (writes to a temp file).
    """
    if isinstance(raw, str) and raw.startswith("data:"):
        _, b64 = raw.split(",", 1)
        payload = base64.b64decode(b64)
        ext = ".bin"
        mime_part = raw.split(";")[0].lower()
        for candidate, guess in [
            ("image/png", ".png"),
            ("image/jpeg", ".jpg"),
            ("image/webp", ".webp"),
            ("audio/wav", ".wav"),
            ("audio/mpeg", ".mp3"),
            ("audio/ogg", ".ogg"),
            ("video/mp4", ".mp4"),
            ("video/webm", ".webm"),
        ]:
            if candidate in mime_part:
                ext = guess
                break
        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(payload)
        tmp.flush()
        tmp.close()
        return Path(tmp.name)

    path = Path(raw)
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    return path


# ---------------------------------------------------------------------------
# MultimodalService
# ---------------------------------------------------------------------------


class MultimodalService:
    """Orchestrates multi-modal input processing across face, vision, STT
    and memory services.

    Design goals:
    * **Partial results** — if one modality fails, the rest continue.
    * **Async-first** — heavy work (vision, I/O) runs via ``asyncio``;
      CPU-bound work (face, STT) runs in a thread executor so the event
      loop is never blocked.
    * **Unified output** — every ``process_input`` call returns the same
      shape regardless of which modalities were supplied.
    """

    def __init__(
        self,
        settings: Settings,
        face_service: _FaceServiceProto,
        stt_service: _STTServiceProto,
        vision_service: _VisionServiceProto,
        memory_service: _MemoryServiceProto,
    ) -> None:
        self._settings = settings
        self._face = face_service
        self._stt = stt_service
        self._vision = vision_service
        self._memory = memory_service

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def process_input(
        self,
        text: str | None = None,
        images: list[str | Path] | None = None,
        audio: str | Path | None = None,
        video: str | Path | None = None,
        *,
        context: str | None = None,
    ) -> dict[str, Any]:
        """Main pipeline entry point.

        Accepts any combination of modalities and returns a unified
        analysis dict.  Each modality is processed independently; a
        failure in one does not affect others.
        """
        meta = _ProcessingMetadata()
        images = images or []

        # --- Collect coroutines for each modality ---
        coros: dict[str, Coroutine] = {}

        if text:
            coros["text"] = self._process_text(text)

        if images:
            coros["images"] = self._process_images(images)

        if audio:
            coros["audio"] = self._process_audio(audio)

        if video:
            coros["video"] = self._process_video(video)

        if not coros:
            return self._build_result(meta)

        # --- Run all modalities concurrently ---
        results: dict[str, Any] = {}
        outcomes = await asyncio.gather(*coros.values(), return_exceptions=True)

        for modality, outcome in zip(coros.keys(), outcomes):
            if isinstance(outcome, Exception):
                logger.warning(
                    "[%s] %s processing failed: %s",
                    meta.request_id,
                    modality,
                    outcome,
                )
                meta.errors.append(_ModalityError(modality=modality, error=str(outcome)))
            else:
                results[modality] = outcome

        meta.finished_at = time.monotonic()
        return self._build_result(meta, results, context=context)

    async def process_image(self, image: str | Path) -> dict:
        return await self._process_single_image(image)

    async def process_audio(self, audio: str | Path) -> dict:
        return await self._process_audio(audio)

    async def process_video(self, video: str | Path) -> dict:
        return await self._process_video(video)

    # ------------------------------------------------------------------
    # Text
    # ------------------------------------------------------------------

    @staticmethod
    async def _process_text(text: str) -> dict:
        return {
            "text_content": text,
            "word_count": len(text.split()),
            "char_count": len(text),
        }

    # ------------------------------------------------------------------
    # Images  (face recognition + vision analysis)
    # ------------------------------------------------------------------

    async def _process_images(self, images: list[str | Path]) -> dict:
        tasks = [self._process_single_image(img) for img in images]
        outcomes = await asyncio.gather(*tasks, return_exceptions=True)

        visual_analyses: list[dict] = []
        face_matches: list[dict] = []
        errors: list[str] = []

        for i, outcome in enumerate(outcomes):
            if isinstance(outcome, Exception):
                errors.append(f"image[{i}]: {outcome}")
                continue
            result = outcome  # type: ignore[assignment]
            if result.get("visual_analysis"):
                visual_analyses.append(result["visual_analysis"])
            if result.get("face_match"):
                face_matches.append(result["face_match"])

        return {
            "visual_analyses": visual_analyses,
            "face_matches": face_matches,
            "errors": errors,
        }

    async def _process_single_image(self, image: str | Path) -> dict:
        path = _resolve_input_path(image)

        # Face recognition (CPU-bound → thread)
        face_match: dict | None = None
        try:
            embeddings = await self._get_stored_embeddings()
            if embeddings:
                face_match = await asyncio.to_thread(
                    self._face.identify_face,
                    str(path),
                    embeddings,
                )
        except Exception:
            logger.debug("Face identification skipped for %s", path, exc_info=True)

        # Vision analysis (already async)
        visual_analysis: dict | None = None
        try:
            visual_analysis = await self._vision.analyze_image(path)
        except Exception:
            logger.debug("Vision analysis failed for %s", path, exc_info=True)

        return {
            "source": str(image),
            "face_match": face_match,
            "visual_analysis": visual_analysis,
        }

    # ------------------------------------------------------------------
    # Audio  (STT transcription)
    # ------------------------------------------------------------------

    async def _process_audio(self, audio: str | Path) -> dict:
        path = _resolve_input_path(audio)
        result = await asyncio.to_thread(
            self._stt.transcribe,
            path,
        )
        return {
            "source": str(audio),
            "transcript": result.get("text", ""),
            "segments": result.get("segments", []),
            "language": result.get("language"),
            "language_probability": result.get("language_probability"),
            "duration": result.get("duration"),
        }

    # ------------------------------------------------------------------
    # Video  (frame extraction + audio extraction)
    # ------------------------------------------------------------------

    async def _process_video(self, video: str | Path) -> dict:
        path = _resolve_input_path(video)

        # -- Extract frames & audio concurrently --
        frame_task = asyncio.to_thread(_extract_video_frames, path)
        audio_task = asyncio.to_thread(_extract_audio_from_video, path)
        (frame_paths, audio_path) = await asyncio.gather(frame_task, audio_task, return_exceptions=True)

        results: dict[str, Any] = {"source": str(video)}

        # -- Analyse frames --
        if isinstance(frame_paths, list) and frame_paths:
            try:
                frame_analysis = await self._vision.analyze_video_frames(frame_paths)
                results["frame_analysis"] = frame_analysis
            except Exception as exc:
                results["frame_analysis_error"] = str(exc)

            try:
                embeddings = await self._get_stored_embeddings()
                if embeddings:
                    face_match = await asyncio.to_thread(
                        self._face.identify_face,
                        str(frame_paths[0]),
                        embeddings,
                    )
                    results["face_match"] = face_match
            except Exception:
                logger.debug("Face identification from video frame skipped", exc_info=True)
        elif isinstance(frame_paths, Exception):
            results["frame_extraction_error"] = str(frame_paths)

        # -- Transcribe audio track --
        if isinstance(audio_path, Path) and audio_path.exists():
            try:
                transcript = await asyncio.to_thread(
                    self._stt.transcribe,
                    audio_path,
                )
                results["transcript"] = transcript.get("text", "")
                results["segments"] = transcript.get("segments", [])
                results["language"] = transcript.get("language")
                results["duration"] = transcript.get("duration")
            except Exception as exc:
                results["audio_transcription_error"] = str(exc)
        elif isinstance(audio_path, Exception):
            results["audio_extraction_error"] = str(audio_path)

        return results

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    async def _get_stored_embeddings(self) -> list[dict]:
        try:
            return await asyncio.to_thread(self._memory.get_all_face_embeddings)
        except Exception:
            logger.debug("Memory service unavailable, skipping face lookup")
            return []

    # ------------------------------------------------------------------
    # Result builder
    # ------------------------------------------------------------------

    @staticmethod
    def _build_result(
        meta: _ProcessingMetadata,
        results: dict[str, Any] | None = None,
        *,
        context: str | None = None,
    ) -> dict[str, Any]:
        results = results or {}

        # --- text_content ---
        text_parts: list[str] = []
        if "text" in results:
            text_parts.append(results["text"].get("text_content", ""))

        audio_result = results.get("audio")
        if audio_result and audio_result.get("transcript"):
            text_parts.append(audio_result["transcript"])

        video_result = results.get("video")
        if video_result and video_result.get("transcript"):
            text_parts.append(video_result["transcript"])

        text_content = " ".join(t for t in text_parts if t).strip()

        # --- visual_analysis ---
        visual_analysis: list[dict] = []
        img_result = results.get("images")
        if img_result and img_result.get("visual_analyses"):
            visual_analysis.extend(img_result["visual_analyses"])

        single_img = results.get("image")
        if single_img and single_img.get("visual_analysis"):
            visual_analysis.append(single_img["visual_analysis"])

        if video_result and video_result.get("frame_analysis"):
            visual_analysis.append(video_result["frame_analysis"])

        # --- face_matches ---
        face_matches: list[dict] = []
        if img_result and img_result.get("face_matches"):
            face_matches.extend(img_result["face_matches"])
        if single_img and single_img.get("face_match"):
            face_matches.append(single_img["face_match"])
        if video_result and video_result.get("face_match"):
            face_matches.append(video_result["face_match"])

        # --- audio_transcript ---
        audio_transcript: dict | None = None
        if audio_result:
            audio_transcript = {
                "text": audio_result.get("transcript", ""),
                "segments": audio_result.get("segments", []),
                "language": audio_result.get("language"),
                "duration": audio_result.get("duration"),
            }
        elif video_result and video_result.get("transcript"):
            audio_transcript = {
                "text": video_result.get("transcript", ""),
                "segments": video_result.get("segments", []),
                "language": video_result.get("language"),
                "duration": video_result.get("duration"),
            }

        # --- confidence estimation ---
        modality_count = sum(
            1 for key in ("text", "audio", "video") if key in results and not isinstance(results[key], Exception)
        )
        if img_result or single_img:
            modality_count += 1

        error_count = len(meta.errors)
        confidence = (
            round(
                max(0.0, 1.0 - (error_count / max(modality_count, 1)) * 0.5),
                4,
            )
            if modality_count
            else 0.0
        )

        return {
            "text_content": text_content,
            "visual_analysis": visual_analysis,
            "face_matches": [m for m in face_matches if m is not None],
            "audio_transcript": audio_transcript,
            "context": context,
            "metadata": {
                **meta.to_dict(),
                "modalities_processed": list(results.keys()),
                "confidence": confidence,
            },
        }
