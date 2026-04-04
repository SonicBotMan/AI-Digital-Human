"""Knowledge graph router — entity and relationship CRUD for React Flow visualization."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.dependencies import GraphServiceDep, UserAuthDep
from app.models.schemas import (
    KnowledgeEdge,
    KnowledgeGraphResponse,
    KnowledgeNode,
    StandardResponse,
)

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


class EntityCreateRequest(BaseModel):
    """Request body for creating a knowledge-graph entity."""

    entity_type: str = Field(
        min_length=1,
        max_length=64,
        description="Entity type, e.g. 'person', 'concept', 'event'",
    )
    name: str = Field(
        min_length=1,
        max_length=256,
        description="Human-readable entity name",
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value properties",
    )


class RelationshipCreateRequest(BaseModel):
    """Request body for creating a knowledge-graph relationship."""

    source_id: UUID = Field(description="Source entity ID")
    target_id: UUID = Field(description="Target entity ID")
    relationship_type: str = Field(
        min_length=1,
        max_length=128,
        description="Relationship type, e.g. 'knows', 'related_to'",
    )
    strength: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="Relationship strength between 0 and 1",
    )
    attributes: dict[str, Any] = Field(
        default_factory=dict,
        description="Arbitrary key-value properties",
    )


@router.get(
    "/{user_id}/graph",
    response_model=StandardResponse[KnowledgeGraphResponse],
)
async def get_graph(
    user_id: UUID,
    service: GraphServiceDep,
    current_user: UserAuthDep,
    depth: int = Query(default=2, ge=1, le=5, description="BFS traversal depth"),
) -> StandardResponse[KnowledgeGraphResponse]:
    """Get the knowledge graph for a user in React Flow compatible format."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    raw = await service.get_user_subgraph(user_id=user_id, depth=depth)

    nodes = [
        KnowledgeNode(
            id=n["id"],
            label=n.get("label", n.get("name", "")),
            type=n.get("type", "concept"),
            properties=n.get("attributes", {}),
        )
        for n in raw.get("nodes", [])
    ]

    edges = [
        KnowledgeEdge(
            id=e.get("id", f"{e['source']}-{e['target']}"),
            source_id=e["source"],
            target_id=e["target"],
            relationship=e.get("type", "related_to"),
            properties={"strength": e.get("strength", 1.0)},
        )
        for e in raw.get("edges", [])
    ]

    graph = KnowledgeGraphResponse(
        nodes=nodes,
        edges=edges,
        metadata=raw.get("metadata", {}),
    )

    return StandardResponse(
        success=True,
        message="Knowledge graph retrieved",
        data=graph,
    )


@router.get(
    "/{user_id}/entities",
    response_model=StandardResponse[list[KnowledgeNode]],
)
async def list_entities(
    user_id: UUID,
    service: GraphServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[list[KnowledgeNode]]:
    """List all entities in a user's knowledge graph."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    raw = await service.get_user_subgraph(user_id=user_id, depth=0)

    entities = [
        KnowledgeNode(
            id=n["id"],
            label=n.get("label", n.get("name", "")),
            type=n.get("type", "concept"),
            properties=n.get("attributes", {}),
        )
        for n in raw.get("nodes", [])
    ]

    return StandardResponse(
        success=True,
        message="Entities retrieved",
        data=entities,
    )


@router.post(
    "/{user_id}/entities",
    response_model=StandardResponse[KnowledgeNode],
    status_code=201,
)
async def add_entity(
    user_id: UUID,
    body: EntityCreateRequest,
    service: GraphServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[KnowledgeNode]:
    """Add a new entity to the user's knowledge graph."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    entity_id = await service.add_entity(
        user_id=user_id,
        entity_type=body.entity_type,
        name=body.name,
        attributes=body.attributes,
    )
    entity_data = await service.get_entity(entity_id=entity_id)

    node = KnowledgeNode(
        id=entity_data["id"],
        label=entity_data.get("name", body.name),
        type=entity_data.get("entity_type", body.entity_type),
        properties=entity_data.get("attributes", {}),
    )

    return StandardResponse(
        success=True,
        message="Entity created",
        data=node,
    )


@router.get(
    "/{user_id}/relationships",
    response_model=StandardResponse[list[KnowledgeEdge]],
)
async def list_relationships(
    user_id: UUID,
    service: GraphServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[list[KnowledgeEdge]]:
    """List all relationships in a user's knowledge graph."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    raw = await service.get_user_subgraph(user_id=user_id, depth=2)

    edges = [
        KnowledgeEdge(
            id=e.get("id", f"{e['source']}-{e['target']}"),
            source_id=e["source"],
            target_id=e["target"],
            relationship=e.get("type", "related_to"),
            properties={"strength": e.get("strength", 1.0)},
        )
        for e in raw.get("edges", [])
    ]

    return StandardResponse(
        success=True,
        message="Relationships retrieved",
        data=edges,
    )


@router.post(
    "/{user_id}/relationships",
    response_model=StandardResponse[KnowledgeEdge],
    status_code=201,
)
async def add_relationship(
    user_id: UUID,
    body: RelationshipCreateRequest,
    service: GraphServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[KnowledgeEdge]:
    """Add a new relationship between two entities in the knowledge graph."""
    if current_user.id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this resource")
    rel_id = await service.add_relationship(
        source_id=body.source_id,
        target_id=body.target_id,
        rel_type=body.relationship_type,
        strength=body.strength,
        attributes=body.attributes,
    )

    edge = KnowledgeEdge(
        id=rel_id,
        source_id=body.source_id,
        target_id=body.target_id,
        relationship=body.relationship_type,
        properties={**body.attributes, "strength": body.strength},
    )

    return StandardResponse(
        success=True,
        message="Relationship created",
        data=edge,
    )
