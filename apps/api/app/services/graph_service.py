"""Knowledge Graph Service — entity/relationship CRUD, BFS traversal, and LLM extraction."""

from __future__ import annotations

import json
import logging
import uuid
from collections import deque
from typing import Any

import aisuite as ai
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.database import KnowledgeEntity, KnowledgeRelationship

logger = logging.getLogger(__name__)

VALID_ENTITY_TYPES: frozenset[str] = frozenset(
    {"person", "preference", "trait", "location", "activity", "concept", "event"}
)

VALID_RELATIONSHIP_TYPES: frozenset[str] = frozenset(
    {
        "likes",
        "dislikes",
        "has_trait",
        "knows",
        "visited",
        "prefers",
        "related_to",
        "participates_in",
        "located_in",
        "friend_of",
        "works_at",
        "studies_at",
    }
)

_ENTITY_EXTRACTION_PROMPT = """\
You are an entity and relationship extraction engine. Given a text, extract \
entities and relationships in strict JSON format.

Entity types allowed: person, preference, trait, location, activity, concept, event
Relationship types allowed: likes, dislikes, has_trait, knows, visited, prefers, \
related_to, participates_in, located_in, friend_of, works_at, studies_at

Return a JSON object with two keys:
- "entities": list of {"name": str, "type": str, "attributes": {}}
- "relationships": list of {"source_name": str, "target_name": str, "type": str, "strength": float}

Rules:
- Extract ONLY explicitly stated facts.
- "strength" is 0.0–1.0; default to 1.0 for direct statements.
- Normalise names to lowercase.
- Return ONLY the JSON, no markdown fences.
If no entities are found, return {"entities": [], "relationships": []}.
"""


class GraphServiceError(Exception):
    """Raised when a graph operation fails."""


class GraphService:
    """CRUD + traversal operations for the knowledge graph.

    Parameters
    ----------
    db_session:
        An SQLAlchemy ``AsyncSession`` bound to the PostgreSQL database.
    """

    def __init__(self, db_session: AsyncSession) -> None:
        self._session = db_session
        self._llm_client: ai.Client | None = None

    def _get_llm_client(self) -> ai.Client:
        if self._llm_client is None:
            provider_configs: dict[str, Any] = {}
            if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY:
                provider_configs["openai"] = {"api_key": settings.OPENAI_API_KEY}
            elif settings.LLM_PROVIDER == "glm" and settings.GLM_API_KEY:
                provider_configs["glm"] = {"api_key": settings.GLM_API_KEY}
            elif settings.LLM_PROVIDER == "minimax" and settings.MINIMAX_API_KEY:
                provider_configs["minimax"] = {"api_key": settings.MINIMAX_API_KEY}
            else:
                provider_configs["glm"] = {"api_key": settings.GLM_API_KEY or "dummy"}
            self._llm_client = ai.Client(provider_configs=provider_configs)
        return self._llm_client

    async def add_entity(
        self,
        user_id: uuid.UUID,
        entity_type: str,
        name: str,
        attributes: dict[str, Any] | None = None,
    ) -> uuid.UUID:
        """Add an entity, or merge attributes if same user+type+name already exists."""
        entity_type = entity_type.lower().strip()
        name = name.lower().strip()

        stmt = select(KnowledgeEntity).where(
            and_(
                KnowledgeEntity.user_id == user_id,
                KnowledgeEntity.entity_type == entity_type,
                KnowledgeEntity.name == name,
            )
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            if attributes:
                merged = {**(existing.attributes or {}), **attributes}
                existing.attributes = merged
                self._session.add(existing)
            await self._session.flush()
            logger.debug("Deduplicated entity %s (%s)", existing.id, name)
            return existing.id

        entity = KnowledgeEntity(
            user_id=user_id,
            entity_type=entity_type,
            name=name,
            attributes=attributes or {},
        )
        self._session.add(entity)
        await self._session.flush()
        logger.info("Created entity %s — type=%s name=%s", entity.id, entity_type, name)
        return entity.id

    async def get_entity(self, entity_id: uuid.UUID) -> dict[str, Any] | None:
        """Return entity details as a dict, or *None* if not found."""
        stmt = select(KnowledgeEntity).where(KnowledgeEntity.id == entity_id)
        result = await self._session.execute(stmt)
        entity = result.scalar_one_or_none()
        if entity is None:
            return None
        return {
            "id": str(entity.id),
            "user_id": str(entity.user_id),
            "entity_type": entity.entity_type,
            "name": entity.name,
            "attributes": entity.attributes or {},
            "created_at": entity.created_at.isoformat() if entity.created_at else None,
        }

    async def add_relationship(
        self,
        source_id: uuid.UUID,
        target_id: uuid.UUID,
        rel_type: str,
        strength: float = 1.0,
        attributes: dict[str, Any] | None = None,
    ) -> uuid.UUID:
        """Add a directed relationship, updating if (source, target, type) already exists."""
        rel_type = rel_type.lower().strip()
        strength = max(0.0, min(1.0, strength))

        stmt = select(KnowledgeRelationship).where(
            and_(
                KnowledgeRelationship.source_entity_id == source_id,
                KnowledgeRelationship.target_entity_id == target_id,
                KnowledgeRelationship.relationship_type == rel_type,
            )
        )
        result = await self._session.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            existing.strength = strength
            if attributes:
                existing.attributes = attributes
            self._session.add(existing)
            await self._session.flush()
            logger.debug("Updated relationship %s (%s)", existing.id, rel_type)
            return existing.id

        rel = KnowledgeRelationship(
            source_entity_id=source_id,
            target_entity_id=target_id,
            relationship_type=rel_type,
            strength=strength,
            attributes=attributes or {},
        )
        self._session.add(rel)
        await self._session.flush()
        logger.info(
            "Created relationship %s — %s -> %s [%s]",
            rel.id,
            source_id,
            target_id,
            rel_type,
        )
        return rel.id

    async def get_entity_relationships(self, entity_id: uuid.UUID) -> list[dict[str, Any]]:
        """Get all relationships where entity_id is source or target."""
        outgoing = select(KnowledgeRelationship).where(
            KnowledgeRelationship.source_entity_id == entity_id,
        )
        incoming = select(KnowledgeRelationship).where(
            KnowledgeRelationship.target_entity_id == entity_id,
        )

        results: list[dict[str, Any]] = []

        for stmt in (outgoing, incoming):
            rs = await self._session.execute(stmt)
            for rel in rs.scalars().all():
                results.append(
                    {
                        "id": str(rel.id),
                        "source_id": str(rel.source_entity_id),
                        "target_id": str(rel.target_entity_id),
                        "relationship_type": rel.relationship_type,
                        "strength": rel.strength,
                        "attributes": rel.attributes or {},
                        "direction": ("outgoing" if rel.source_entity_id == entity_id else "incoming"),
                    }
                )

        return results

    async def get_user_subgraph(
        self,
        user_id: uuid.UUID,
        depth: int = 2,
    ) -> dict[str, Any]:
        """BFS from user's entities up to *depth* hops. Returns React Flow compatible subgraph."""
        depth = max(1, min(5, depth))

        seed_stmt = select(KnowledgeEntity).where(
            KnowledgeEntity.user_id == user_id,
        )
        seed_result = await self._session.execute(seed_stmt)
        seed_entities = list(seed_result.scalars().all())

        if not seed_entities:
            return {"nodes": [], "edges": [], "metadata": {"depth": depth, "node_count": 0, "edge_count": 0}}

        visited_entity_ids: set[uuid.UUID] = set()
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        queue: deque[tuple[uuid.UUID, int]] = deque()

        for entity in seed_entities:
            queue.append((entity.id, 0))

        while queue:
            current_id, current_depth = queue.popleft()
            if current_id in visited_entity_ids:
                continue
            visited_entity_ids.add(current_id)

            ent_stmt = select(KnowledgeEntity).where(KnowledgeEntity.id == current_id)
            ent_result = await self._session.execute(ent_stmt)
            entity = ent_result.scalar_one_or_none()
            if entity is None:
                continue

            nodes.append(
                {
                    "id": str(entity.id),
                    "type": entity.entity_type,
                    "label": entity.name,
                    "attributes": entity.attributes or {},
                }
            )

            if current_depth >= depth:
                continue

            rels = await self._get_relationships_for_entity(entity.id)
            for rel in rels:
                edges.append(
                    {
                        "source": str(rel.source_entity_id),
                        "target": str(rel.target_entity_id),
                        "type": rel.relationship_type,
                        "strength": rel.strength,
                    }
                )

                neighbour_id = rel.target_entity_id if rel.source_entity_id == current_id else rel.source_entity_id
                if neighbour_id not in visited_entity_ids:
                    queue.append((neighbour_id, current_depth + 1))

        seen_edges: set[tuple[str, str, str]] = set()
        unique_edges: list[dict[str, Any]] = []
        for edge in edges:
            key = (edge["source"], edge["target"], edge["type"])
            if key not in seen_edges:
                seen_edges.add(key)
                unique_edges.append(edge)

        return {
            "nodes": nodes,
            "edges": unique_edges,
            "metadata": {
                "depth": depth,
                "node_count": len(nodes),
                "edge_count": len(unique_edges),
            },
        }

    async def _get_relationships_for_entity(self, entity_id: uuid.UUID) -> list[KnowledgeRelationship]:
        out_stmt = select(KnowledgeRelationship).where(
            KnowledgeRelationship.source_entity_id == entity_id,
        )
        in_stmt = select(KnowledgeRelationship).where(
            KnowledgeRelationship.target_entity_id == entity_id,
        )

        relationships: list[KnowledgeRelationship] = []
        for stmt in (out_stmt, in_stmt):
            rs = await self._session.execute(stmt)
            relationships.extend(rs.scalars().all())
        return relationships

    async def extract_entities_from_text(
        self,
        text: str,
        user_id: uuid.UUID,
    ) -> list[dict[str, Any]]:
        """Extract entities and relationships from text via LLM, persisting to the graph."""
        client = self._get_llm_client()
        model = settings.DEFAULT_LLM_MODEL

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": _ENTITY_EXTRACTION_PROMPT},
                    {"role": "user", "content": text},
                ],
                max_tokens=2048,
                temperature=0.1,
            )
            raw = response.choices[0].message.content or ""
        except Exception as exc:
            logger.exception("Entity extraction LLM call failed")
            raise GraphServiceError(f"LLM entity extraction failed: {exc}") from exc

        # Strip markdown code fences if the LLM wrapped its output
        raw = raw.strip()
        if raw.startswith("```"):
            first_newline = raw.index("\n")
            last_fence = raw.rfind("```")
            raw = raw[first_newline + 1 : last_fence].strip()

        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError as exc:
            logger.warning("Failed to parse LLM entity extraction output: %s", exc)
            return []

        raw_entities = parsed.get("entities", [])
        raw_relationships = parsed.get("relationships", [])

        name_to_id: dict[str, uuid.UUID] = {}
        created_entities: list[dict[str, Any]] = []

        for ent in raw_entities:
            name = ent.get("name", "").strip().lower()
            etype = ent.get("type", "concept").strip().lower()
            attrs = ent.get("attributes", {})
            if not name:
                continue

            entity_id = await self.add_entity(
                user_id=user_id,
                entity_type=etype,
                name=name,
                attributes=attrs,
            )
            name_to_id[name] = entity_id
            created_entities.append({"id": str(entity_id), "name": name, "type": etype})

        created_relationships: list[dict[str, Any]] = []
        for rel in raw_relationships:
            src_name = rel.get("source_name", "").strip().lower()
            tgt_name = rel.get("target_name", "").strip().lower()
            rel_type = rel.get("type", "related_to").strip().lower()
            strength = float(rel.get("strength", 1.0))

            src_id = name_to_id.get(src_name)
            tgt_id = name_to_id.get(tgt_name)
            if src_id is None or tgt_id is None:
                logger.debug(
                    "Skipping relationship — unmapped entity: %s -> %s",
                    src_name,
                    tgt_name,
                )
                continue

            rel_id = await self.add_relationship(
                source_id=src_id,
                target_id=tgt_id,
                rel_type=rel_type,
                strength=strength,
            )
            created_relationships.append(
                {
                    "id": str(rel_id),
                    "source": src_name,
                    "target": tgt_name,
                    "type": rel_type,
                }
            )

        return [{"entities": created_entities, "relationships": created_relationships}]

    async def build_user_profile(self, user_id: uuid.UUID) -> dict[str, Any]:
        """Aggregate the knowledge graph into a structured user profile for chat context enrichment."""
        stmt = select(KnowledgeEntity).where(KnowledgeEntity.user_id == user_id)
        result = await self._session.execute(stmt)
        all_entities = list(result.scalars().all())

        if not all_entities:
            return {"user_id": str(user_id), "summary": "No knowledge graph data available.", "categories": {}}

        entity_map: dict[uuid.UUID, KnowledgeEntity] = {e.id: e for e in all_entities}

        categories: dict[str, list[dict[str, Any]]] = {}
        for entity in all_entities:
            entry: dict[str, Any] = {
                "id": str(entity.id),
                "name": entity.name,
                "attributes": entity.attributes or {},
                "relationships": [],
            }
            categories.setdefault(entity.entity_type, []).append(entry)

        for entity in all_entities:
            rels = await self._get_relationships_for_entity(entity.id)
            for rel in rels:
                neighbour_id = rel.target_entity_id if rel.source_entity_id == entity.id else rel.source_entity_id
                neighbour = entity_map.get(neighbour_id)
                neighbour_name = neighbour.name if neighbour else str(neighbour_id)
                direction = "to" if rel.source_entity_id == entity.id else "from"

                for cat_entries in categories.values():
                    for entry in cat_entries:
                        if entry["id"] == str(entity.id):
                            entry["relationships"].append(
                                {
                                    "direction": direction,
                                    "type": rel.relationship_type,
                                    "target": neighbour_name,
                                    "strength": rel.strength,
                                }
                            )

        summary_parts: list[str] = []
        entity_type_labels = {
            "person": "People",
            "preference": "Preferences",
            "trait": "Traits",
            "location": "Locations",
            "activity": "Activities",
            "concept": "Concepts",
            "event": "Events",
        }
        for etype, entries in categories.items():
            label = entity_type_labels.get(etype, etype.capitalize())
            names = [e["name"] for e in entries]
            if names:
                summary_parts.append(f"{label}: {', '.join(names)}")

        summary = "; ".join(summary_parts) if summary_parts else "Profile built from knowledge graph."

        return {
            "user_id": str(user_id),
            "summary": summary,
            "categories": categories,
            "entity_count": len(all_entities),
        }
