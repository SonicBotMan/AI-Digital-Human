from __future__ import annotations

import base64
import logging
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

from app.core.config import Settings

logger = logging.getLogger(__name__)

MIN_FACE_SIZE = 30
MIN_DETECTION_CONFIDENCE = 0.5


def _decode_image(image_input: str | Path | np.ndarray) -> np.ndarray:
    if isinstance(image_input, np.ndarray):
        return image_input

    if isinstance(image_input, Path) or (isinstance(image_input, str) and not image_input.startswith("data:")):
        path = Path(image_input)
        if not path.exists():
            raise FileNotFoundError(f"Image file not found: {path}")
        img = cv2.imread(str(path), cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(f"cv2 cannot decode image: {path}")
        return img

    # base64 data URI: data:image/jpeg;base64,....
    if isinstance(image_input, str) and image_input.startswith("data:"):
        _, b64_data = image_input.split(",", 1)
        raw = base64.b64decode(b64_data)
    else:
        raw = base64.b64decode(image_input)

    arr = np.frombuffer(raw, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Cannot decode base64 image data")
    return img


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


class FaceService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._app: FaceAnalysis | None = None
        self._threshold = settings.FACE_SIMILARITY_THRESHOLD
        self._embedding_dim = settings.FACE_EMBEDDING_DIM

    def _get_app(self) -> FaceAnalysis:
        if self._app is not None:
            return self._app

        logger.info(
            "Loading InsightFace model=%s root=%s",
            self._settings.FACE_RECOGNITION_MODEL,
            self._settings.INSIGHTFACE_MODEL_ROOT,
        )
        app = FaceAnalysis(
            name=self._settings.FACE_RECOGNITION_MODEL,
            root=self._settings.INSIGHTFACE_MODEL_ROOT,
        )
        app.prepare(ctx_id=0, det_size=(640, 640))
        self._app = app
        return app

    def extract_embedding(self, image_input: str | Path | np.ndarray) -> np.ndarray:
        img = _decode_image(image_input)
        faces = self._get_app().get(img)

        if not faces:
            raise ValueError("No face detected in image")

        face = max(faces, key=lambda f: f.bbox[2] - f.bbox[0])

        bbox = face.bbox.astype(int)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        if w < MIN_FACE_SIZE or h < MIN_FACE_SIZE:
            raise ValueError(f"Face too small ({w}x{h}px), minimum is {MIN_FACE_SIZE}px")

        if face.det_score is not None and face.det_score < MIN_DETECTION_CONFIDENCE:
            raise ValueError(f"Low detection confidence ({face.det_score:.2f}), minimum is {MIN_DETECTION_CONFIDENCE}")

        embedding = face.embedding
        if embedding is None:
            raise ValueError("Face detected but embedding extraction failed")

        if embedding.shape[0] != self._embedding_dim:
            logger.warning(
                "Embedding dim=%d, expected=%d — normalising",
                embedding.shape[0],
                self._embedding_dim,
            )

        return embedding.astype(np.float32)

    def compare_faces(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        return _cosine_similarity(
            embedding1.astype(np.float32),
            embedding2.astype(np.float32),
        )

    def identify_face(
        self,
        image_input: str | Path | np.ndarray,
        stored_embeddings: list[dict],
        threshold: float | None = None,
    ) -> dict | None:
        query_embedding = self.extract_embedding(image_input)
        thresh = threshold if threshold is not None else self._threshold

        best_match: dict | None = None
        best_score = -1.0

        for record in stored_embeddings:
            stored_emb = np.array(record["embedding"], dtype=np.float32)
            score = _cosine_similarity(query_embedding, stored_emb)
            if score > best_score:
                best_score = score
                best_match = record

        if best_score < thresh:
            return None

        return {
            **best_match,
            "similarity": round(best_score, 4),
        }

    def register_face(
        self,
        user_id: str,
        image_input: str | Path | np.ndarray,
        name: str = "",
    ) -> dict:
        embedding = self.extract_embedding(image_input)
        return {
            "user_id": user_id,
            "name": name,
            "embedding": embedding.tolist(),
            "dim": embedding.shape[0],
        }
