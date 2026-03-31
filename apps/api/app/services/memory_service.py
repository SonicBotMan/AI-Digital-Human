from __future__ import annotations

import logging
import uuid
from typing import Any

import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from app.core.config import Settings

logger = logging.getLogger(__name__)

FACE_COLLECTION = "face_embeddings"
MEMORY_COLLECTION = "conversation_memories"
PROFILE_COLLECTION = "user_profiles"


def _to_list(embedding: list[float] | np.ndarray) -> list[float]:
    return embedding.tolist() if isinstance(embedding, np.ndarray) else list(embedding)


class MemoryService:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: QdrantClient | None = None
        self._face_dim: int = settings.FACE_EMBEDDING_DIM
        self._memory_dim: int = settings.MEMORY_EMBEDDING_DIM
        self._face_threshold: float = settings.FACE_SIMILARITY_THRESHOLD

    def _get_client(self) -> QdrantClient:
        if self._client is not None:
            return self._client

        logger.info(
            "Connecting to Qdrant at %s:%d (gRPC %d)",
            self._settings.QDRANT_HOST,
            self._settings.QDRANT_PORT,
            self._settings.QDRANT_GRPC_PORT,
        )
        self._client = QdrantClient(
            host=self._settings.QDRANT_HOST,
            port=self._settings.QDRANT_PORT,
            grpc_port=self._settings.QDRANT_GRPC_PORT,
            prefer_grpc=True,
        )
        return self._client

    def _ensure_collection(self, name: str, dim: int, distance: Distance = Distance.COSINE) -> None:
        client = self._get_client()
        existing = {c.name for c in client.get_collections().collections}
        if name in existing:
            return
        logger.info("Creating Qdrant collection %q (dim=%d)", name, dim)
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=dim, distance=distance),
        )

    def store_face_embedding(
        self,
        user_id: str,
        embedding: list[float] | np.ndarray,
        name: str = "",
    ) -> str:
        self._ensure_collection(FACE_COLLECTION, self._face_dim)

        point_id = uuid.uuid4().hex
        self._get_client().upsert(
            collection_name=FACE_COLLECTION,
            points=[
                PointStruct(
                    id=point_id,
                    vector=_to_list(embedding),
                    payload={"user_id": user_id, "name": name},
                )
            ],
        )
        logger.debug("Stored face embedding point=%s user=%s", point_id, user_id)
        return point_id

    def search_face(
        self,
        embedding: list[float] | np.ndarray,
        threshold: float | None = None,
    ) -> dict[str, Any] | None:
        self._ensure_collection(FACE_COLLECTION, self._face_dim)

        thresh = threshold if threshold is not None else self._face_threshold
        hits = self._get_client().search(
            collection_name=FACE_COLLECTION,
            query_vector=_to_list(embedding),
            limit=1,
        )
        if not hits:
            return None

        best = hits[0]
        if best.score < thresh:
            return None

        return {**best.payload, "score": round(best.score, 4), "point_id": best.id}

    def store_memory(
        self,
        user_id: str,
        content: str,
        embedding: list[float] | np.ndarray,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        self._ensure_collection(MEMORY_COLLECTION, self._memory_dim)

        point_id = uuid.uuid4().hex
        payload: dict[str, Any] = {"user_id": user_id, "content": content, **(metadata or {})}

        self._get_client().upsert(
            collection_name=MEMORY_COLLECTION,
            points=[PointStruct(id=point_id, vector=_to_list(embedding), payload=payload)],
        )
        logger.debug("Stored memory point=%s user=%s", point_id, user_id)
        return point_id

    def search_memories(
        self,
        user_id: str,
        query_embedding: list[float] | np.ndarray,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        self._ensure_collection(MEMORY_COLLECTION, self._memory_dim)

        hits = self._get_client().search(
            collection_name=MEMORY_COLLECTION,
            query_vector=_to_list(query_embedding),
            query_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
            limit=limit,
        )
        return [{**hit.payload, "score": round(hit.score, 4), "point_id": hit.id} for hit in hits]

    def get_user_profile(self, user_id: str) -> dict[str, Any] | None:
        self._ensure_collection(PROFILE_COLLECTION, self._memory_dim)

        client = self._get_client()
        points, _ = client.scroll(
            collection_name=PROFILE_COLLECTION,
            scroll_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
            limit=1,
            with_payload=True,
            with_vectors=False,
        )
        if not points:
            return None
        return points[0].payload  # type: ignore[return-value]

    def update_user_profile(self, user_id: str, data: dict[str, Any]) -> bool:
        self._ensure_collection(PROFILE_COLLECTION, self._memory_dim)

        client = self._get_client()

        existing, _ = client.scroll(
            collection_name=PROFILE_COLLECTION,
            scroll_filter=Filter(must=[FieldCondition(key="user_id", match=MatchValue(value=user_id))]),
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        if existing:
            point_id = existing[0].id
            payload = {**existing[0].payload, **data, "user_id": user_id}
        else:
            point_id = uuid.uuid4().hex
            payload = {**data, "user_id": user_id}

        zero_vector = [0.0] * self._memory_dim

        client.upsert(
            collection_name=PROFILE_COLLECTION,
            points=[PointStruct(id=point_id, vector=zero_vector, payload=payload)],
        )
        logger.debug("Updated profile for user=%s", user_id)
        return True
