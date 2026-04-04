"""Face recognition API router.

Handles face registration, identification, and person profile management.
All heavy lifting is delegated to FaceService (embedding extraction/comparison)
and MemoryService (vector storage/retrieval).
"""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.dependencies import FaceServiceDep, MemoryServiceDep, UserAuthDep
from app.models.schemas import (
    ErrorResponse,
    FaceIdentifyRequest,
    FaceMatchResult,
    FaceRegisterRequest,
    FaceRegisterResponse,
    PersonProfileBrief,
    PersonProfileDetail,
    PersonProfileUpdate,
    StandardResponse,
    ThoughtChainNode,
    ThoughtType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/faces", tags=["faces"])

# Allowed MIME types for uploaded images
_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _validate_content_type(content_type: str | None, filename: str | None) -> None:
    """Raise 400 if the uploaded file is not a supported image format."""
    if content_type and content_type in _ALLOWED_CONTENT_TYPES:
        return

    if filename:
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if f".{ext}" in _ALLOWED_EXTENSIONS:
            return

    raise HTTPException(
        status_code=400,
        detail=(
            f"Invalid image format. Allowed: JPEG, PNG, WebP. "
            f"Received content_type={content_type!r}, filename={filename!r}"
        ),
    )


def _build_thought_chain(steps: list[dict[str, str]]) -> list[ThoughtChainNode]:
    """Build a thought-chain visualization from processing step labels."""
    nodes: list[ThoughtChainNode] = []
    for idx, step in enumerate(steps):
        node = ThoughtChainNode(
            id=uuid.uuid4(),
            label=step.get("label", f"Step {idx + 1}"),
            type=ThoughtType(step.get("type", "action")),
            content=step.get("content", ""),
            connections=[],
        )
        nodes.append(node)

    for i in range(len(nodes) - 1):
        nodes[i].connections.append(nodes[i + 1].id)

    return nodes


# ---------------------------------------------------------------------------
# POST /faces/register  —  multipart/form-data
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=StandardResponse[FaceRegisterResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image format"},
        422: {"model": ErrorResponse, "description": "No face detected in image"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Register a new face",
)
async def register_face_upload(
    face_service: FaceServiceDep,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
    name: Annotated[str, Form(min_length=1, max_length=128, description="Full name of the person")],
    image: Annotated[UploadFile, File(description="Face image (JPEG, PNG, or WebP)")],
) -> StandardResponse[FaceRegisterResponse]:
    """Register a new person by uploading a face image (multipart/form-data)."""
    _validate_content_type(image.content_type, image.filename)

    try:
        raw_bytes = await image.read()
    except Exception as exc:
        logger.exception("Failed to read uploaded image")
        raise HTTPException(status_code=400, detail="Cannot read uploaded file") from exc

    return await _do_register(face_service, memory_service, name, raw_bytes)


# ---------------------------------------------------------------------------
# POST /faces/register  —  JSON with base64 image
# ---------------------------------------------------------------------------


@router.post(
    "/register",
    response_model=StandardResponse[FaceRegisterResponse],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image format"},
        422: {"model": ErrorResponse, "description": "No face detected in image"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Register a new face (JSON)",
    include_in_schema=False,
)
async def register_face_json(
    face_service: FaceServiceDep,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
    body: FaceRegisterRequest,
) -> StandardResponse[FaceRegisterResponse]:
    """Register a new person by sending a base64-encoded face image (JSON body)."""
    import base64

    image_input = body.image

    if image_input.startswith("data:"):
        _, b64_data = image_input.split(",", 1)
        raw_bytes = base64.b64decode(b64_data)
    else:
        raw_bytes = base64.b64decode(image_input)

    return await _do_register(face_service, memory_service, body.name, raw_bytes)


async def _do_register(
    face_service: Any,
    memory_service: Any,
    name: str,
    raw_bytes: bytes,
) -> StandardResponse[FaceRegisterResponse]:
    """Shared registration logic for both multipart and JSON paths."""
    user_id = uuid.uuid4()

    try:
        result = face_service.register_face(
            user_id=str(user_id),
            image_input=raw_bytes,
            name=name,
        )
    except ValueError as exc:
        msg = str(exc)
        if "No face detected" in msg:
            raise HTTPException(status_code=422, detail=msg) from exc
        if "Cannot decode" in msg or "too small" in msg:
            raise HTTPException(status_code=400, detail=msg) from exc
        raise HTTPException(status_code=422, detail=msg) from exc
    except Exception as exc:
        logger.exception("Face registration failed for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Face processing failed") from exc

    try:
        embedding = result["embedding"]
        face_point_id = memory_service.store_face_embedding(
            user_id=str(user_id),
            embedding=embedding,
            name=name,
        )
    except Exception as exc:
        logger.exception("Failed to store face embedding for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Storage operation failed") from exc

    try:
        memory_service.update_user_profile(
            user_id=str(user_id),
            data={"name": name, "face_registered": True},
        )
    except Exception:
        logger.warning("Could not initialise profile for user=%s", user_id, exc_info=True)

    response_data = FaceRegisterResponse(
        user_id=user_id,
        name=name,
        face_id=uuid.UUID(face_point_id) if len(face_point_id) == 36 else uuid.uuid4(),
    )

    return StandardResponse(
        success=True,
        message="Face registered successfully",
        data=response_data,
    )


# ---------------------------------------------------------------------------
# POST /faces/identify  —  multipart/form-data
# ---------------------------------------------------------------------------


@router.post(
    "/identify",
    response_model=StandardResponse[dict],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image format"},
        422: {"model": ErrorResponse, "description": "No face detected in image"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Identify a person from a face image",
)
async def identify_face_upload(
    face_service: FaceServiceDep,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
    image: Annotated[UploadFile, File(description="Face image to identify (JPEG, PNG, or WebP)")],
    top_k: Annotated[int, Form(ge=1, le=10)] = 1,
) -> StandardResponse[dict]:
    """Identify a person by uploading a face image (multipart/form-data)."""
    _validate_content_type(image.content_type, image.filename)

    try:
        raw_bytes = await image.read()
    except Exception as exc:
        logger.exception("Failed to read uploaded image")
        raise HTTPException(status_code=400, detail="Cannot read uploaded file") from exc

    return await _do_identify(face_service, memory_service, raw_bytes, top_k)


# ---------------------------------------------------------------------------
# POST /faces/identify  —  JSON with base64 image
# ---------------------------------------------------------------------------


@router.post(
    "/identify",
    response_model=StandardResponse[dict],
    responses={
        400: {"model": ErrorResponse, "description": "Invalid image format"},
        422: {"model": ErrorResponse, "description": "No face detected in image"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Identify a person from a face image (JSON)",
    include_in_schema=False,
)
async def identify_face_json(
    face_service: FaceServiceDep,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
    body: FaceIdentifyRequest,
) -> StandardResponse[dict]:
    """Identify a person by sending a base64-encoded face image (JSON body)."""
    import base64

    image_input = body.image
    if image_input.startswith("data:"):
        _, b64_data = image_input.split(",", 1)
        raw_bytes = base64.b64decode(b64_data)
    else:
        raw_bytes = base64.b64decode(image_input)

    return await _do_identify(face_service, memory_service, raw_bytes, body.top_k)


async def _do_identify(
    face_service: Any,
    memory_service: Any,
    raw_bytes: bytes,
    top_k: int = 1,
) -> StandardResponse[dict]:
    """Shared identification logic."""
    try:
        query_embedding = face_service.extract_embedding(raw_bytes)
    except ValueError as exc:
        msg = str(exc)
        if "No face detected" in msg:
            raise HTTPException(status_code=422, detail=msg) from exc
        raise HTTPException(status_code=400, detail=msg) from exc
    except Exception as exc:
        logger.exception("Face embedding extraction failed")
        raise HTTPException(status_code=500, detail="Face processing failed") from exc

    try:
        search_result = memory_service.search_face(embedding=query_embedding)
    except Exception as exc:
        logger.exception("Face search failed")
        raise HTTPException(status_code=500, detail="Search operation failed") from exc

    thought_steps = [
        {"label": "Image Received", "type": "observation", "content": "Face image uploaded for identification"},
        {
            "label": "Face Detection",
            "type": "action",
            "content": "Detected face region and extracted 512-dim embedding",
        },
        {
            "label": "Vector Search",
            "type": "reasoning",
            "content": "Searched stored face embeddings using cosine similarity",
        },
        {"label": "Match Decision", "type": "decision", "content": "Compared similarity score against threshold"},
    ]

    matches: list[dict[str, Any]] = []

    if search_result:
        matched_user_id = search_result.get("user_id", "")
        matched_name = search_result.get("name", "Unknown")
        score = search_result.get("score", 0.0)

        profile_data = memory_service.get_user_profile(str(matched_user_id))
        profile_brief: PersonProfileBrief | None = None
        if profile_data:
            profile_brief = PersonProfileBrief(
                user_id=uuid.UUID(matched_user_id),
                name=profile_data.get("name", matched_name),
                gender=profile_data.get("gender"),
                avatar_url=profile_data.get("avatar_url"),
            )

        matches.append(
            FaceMatchResult(
                user_id=uuid.UUID(matched_user_id),
                name=matched_name,
                confidence=score,
                profile=profile_brief,
            ).model_dump()
        )

        thought_steps.append(
            {
                "label": "Identified",
                "type": "reflection",
                "content": f"Best match: {matched_name} with confidence {score:.2%}",
            }
        )
    else:
        thought_steps.append(
            {
                "label": "No Match",
                "type": "reflection",
                "content": "No face matched above the similarity threshold",
            }
        )

    thought_chain = _build_thought_chain(thought_steps)

    return StandardResponse(
        success=True,
        message="Identification complete" if matches else "No matching face found",
        data={
            "matches": matches,
            "match_count": len(matches),
            "thought_chain": [node.model_dump(mode="json") for node in thought_chain],
        },
    )


# ---------------------------------------------------------------------------
# GET /faces/{user_id}  —  Get user profile
# ---------------------------------------------------------------------------


@router.get(
    "/{user_id}",
    response_model=StandardResponse[PersonProfileDetail],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Get user profile",
)
async def get_user_profile(
    user_id: uuid.UUID,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[PersonProfileDetail]:
    """Retrieve the full profile of a registered person."""
    try:
        profile_data = memory_service.get_user_profile(str(user_id))
    except Exception as exc:
        logger.exception("Failed to fetch profile for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Storage operation failed") from exc

    if profile_data is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    profile = PersonProfileDetail(
        user_id=user_id,
        name=profile_data.get("name", ""),
        gender=profile_data.get("gender"),
        avatar_url=profile_data.get("avatar_url"),
        appearance_features=profile_data.get("appearance_features", {}),
        speaking_style=profile_data.get("speaking_style", {}),
        preferences=profile_data.get("preferences", {}),
        personality_traits=profile_data.get("personality_traits", []),
        notes=profile_data.get("notes"),
        face_registered=profile_data.get("face_registered", False),
        created_at=profile_data.get("created_at"),
        updated_at=profile_data.get("updated_at"),
    )

    return StandardResponse(
        success=True,
        message="Profile retrieved successfully",
        data=profile,
    )


# ---------------------------------------------------------------------------
# PUT /faces/{user_id}  —  Update user profile
# ---------------------------------------------------------------------------


@router.put(
    "/{user_id}",
    response_model=StandardResponse[PersonProfileDetail],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Update user profile",
)
async def update_user_profile(
    user_id: uuid.UUID,
    body: PersonProfileUpdate,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[PersonProfileDetail]:
    """Update the profile of an existing registered person."""
    try:
        existing = memory_service.get_user_profile(str(user_id))
    except Exception as exc:
        logger.exception("Failed to fetch profile for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Storage operation failed") from exc

    if existing is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    update_data: dict[str, Any] = {"user_id": str(user_id)}
    for field_name, value in body.model_dump(exclude_unset=True).items():
        update_data[field_name] = value

    try:
        memory_service.update_user_profile(str(user_id), update_data)
    except Exception as exc:
        logger.exception("Failed to update profile for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Storage operation failed") from exc

    updated_data = memory_service.get_user_profile(str(user_id))
    profile = PersonProfileDetail(
        user_id=user_id,
        name=updated_data.get("name", existing.get("name", "")) if updated_data else existing.get("name", ""),
        gender=updated_data.get("gender") if updated_data else existing.get("gender"),
        avatar_url=updated_data.get("avatar_url") if updated_data else existing.get("avatar_url"),
        appearance_features=(updated_data or existing).get("appearance_features", {}),
        speaking_style=(updated_data or existing).get("speaking_style", {}),
        preferences=(updated_data or existing).get("preferences", {}),
        personality_traits=(updated_data or existing).get("personality_traits", []),
        notes=(updated_data or existing).get("notes"),
        face_registered=(updated_data or existing).get("face_registered", False),
        created_at=(updated_data or existing).get("created_at"),
        updated_at=(updated_data or existing).get("updated_at"),
    )

    return StandardResponse(
        success=True,
        message="Profile updated successfully",
        data=profile,
    )


# ---------------------------------------------------------------------------
# DELETE /faces/{user_id}  —  Delete user
# ---------------------------------------------------------------------------


@router.delete(
    "/{user_id}",
    response_model=StandardResponse[None],
    responses={
        404: {"model": ErrorResponse, "description": "User not found"},
        500: {"model": ErrorResponse, "description": "Processing error"},
    },
    summary="Delete a registered person",
)
async def delete_user(
    user_id: uuid.UUID,
    memory_service: MemoryServiceDep,
    current_user: UserAuthDep,
) -> StandardResponse[None]:
    """Delete a registered person and all associated face data."""
    try:
        profile_data = memory_service.get_user_profile(str(user_id))
    except Exception as exc:
        logger.exception("Failed to fetch profile for user=%s", user_id)
        raise HTTPException(status_code=500, detail="Storage operation failed") from exc

    if profile_data is None:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")

    try:
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        client = memory_service._get_client()
        from app.services.memory_service import PROFILE_COLLECTION, FACE_COLLECTION

        client.delete(
            collection_name=FACE_COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))],
            ),
        )

        client.delete(
            collection_name=PROFILE_COLLECTION,
            points_selector=Filter(
                must=[FieldCondition(key="user_id", match=MatchValue(value=str(user_id)))],
            ),
        )
    except Exception as exc:
        logger.exception("Failed to delete user=%s", user_id)
        raise HTTPException(status_code=500, detail="Deletion operation failed") from exc

    return StandardResponse(
        success=True,
        message=f"User {user_id} deleted successfully",
        data=None,
    )
