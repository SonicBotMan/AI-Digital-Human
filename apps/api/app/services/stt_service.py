from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path

from faster_whisper import WhisperModel

from app.core.config import Settings

logger = logging.getLogger(__name__)

AUDIO_EXTENSIONS = frozenset(
    {
        ".wav",
        ".mp3",
        ".flac",
        ".ogg",
        ".opus",
        ".m4a",
        ".aac",
        ".wma",
        ".webm",
    }
)


def _audio_to_wav_bytes(audio_path: str | Path) -> bytes:
    """Convert any audio to 16 kHz mono WAV via ffmpeg."""
    import subprocess

    result = subprocess.run(
        [
            "ffmpeg",
            "-i",
            str(audio_path),
            "-vn",  # no video
            "-ar",
            "16000",  # 16 kHz sample rate
            "-ac",
            "1",  # mono
            "-f",
            "wav",
            "-acodec",
            "pcm_s16le",
            "-hide_banner",
            "-loglevel",
            "error",
            "pipe:1",
        ],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed (rc={result.returncode}): {result.stderr.decode(errors='replace')}")
    return result.stdout


def _looks_like_audio(path: str | Path) -> bool:
    return Path(path).suffix.lower() in AUDIO_EXTENSIONS


class STTService:
    def __init__(self, settings: Settings) -> None:
        device = settings.WHISPER_DEVICE
        compute_type = settings.WHISPER_COMPUTE_TYPE

        if device == "auto":
            device = "cuda" if self._cuda_available() else "cpu"
            if device == "cpu":
                compute_type = "int8"

        logger.info(
            "Loading faster-whisper model=%s device=%s compute=%s",
            settings.WHISPER_MODEL_SIZE,
            device,
            compute_type,
        )
        self._model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            device=device,
            compute_type=compute_type,
        )
        self._settings = settings

    @staticmethod
    def _cuda_available() -> bool:
        try:
            import torch  # noqa: F401

            return torch.cuda.is_available()
        except ImportError:
            return False

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> dict:
        path = Path(audio_path)
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")

        wav_bytes = _audio_to_wav_bytes(path)
        return self.transcribe_from_bytes(wav_bytes, language=language)

    def transcribe_from_bytes(
        self,
        audio_bytes: bytes,
        language: str | None = None,
    ) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            segments_iter, info = self._model.transcribe(
                tmp.name,
                language=language,
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=500,
                    speech_pad_ms=200,
                ),
                word_timestamps=False,
            )

            segments = []
            for seg in segments_iter:
                segments.append(
                    {
                        "start": round(seg.start, 3),
                        "end": round(seg.end, 3),
                        "text": seg.text.strip(),
                    }
                )

        full_text = " ".join(s["text"] for s in segments).strip()

        return {
            "text": full_text,
            "segments": segments,
            "language": info.language,
            "language_probability": round(info.language_probability, 4),
            "duration": round(info.duration, 3),
        }

    def transcribe_audio_or_extract(
        self,
        media_path: str | Path,
        language: str | None = None,
    ) -> dict:
        path = Path(media_path)
        if not path.exists():
            raise FileNotFoundError(f"Media file not found: {path}")

        if _looks_like_audio(path):
            wav_bytes = _audio_to_wav_bytes(path)
        else:
            wav_bytes = _audio_to_wav_bytes(path)

        return self.transcribe_from_bytes(wav_bytes, language=language)
