"""Pydantic v2 request/response schemas for the AI Digital Human API.

Used by FastAPI for request validation and response serialization.
These schemas are shared with the frontend via OpenAPI spec generation.
"""

import enum
from datetime import datetime
from typing import Any, Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class ThoughtType(str, enum.Enum):
    """Types of nodes in a thought chain."""

    OBSERVATION = "observation"
    REASONING = "reasoning"
    HYPOTHESIS = "hypothesis"
    DECISION = "decision"
    ACTION = "action"
    REFLECTION = "reflection"


class ModalityType(str, enum.Enum):
    """Supported modalities for multimodal analysis."""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


class PersonGender(str, enum.Enum):
    """Gender options for person profiles."""

    MALE = "male"
    FEMALE = "female"
    OTHER = "other"
    UNSPECIFIED = "unspecified"


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Common Pydantic config shared by every schema."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        str_strip_whitespace=True,
    )


# ---------------------------------------------------------------------------
# Generic wrapper responses
# ---------------------------------------------------------------------------


class StandardResponse(BaseSchema, Generic[T]):
    """Generic API envelope returned by most endpoints."""

    success: bool = Field(description="Whether the request was successful")
    message: str = Field(description="Human-readable status message")
    data: T | None = Field(default=None, description="Payload")


class ErrorResponse(BaseSchema):
    """Standard error envelope."""

    error: str = Field(description="Short error identifier, e.g. 'not_found'")
    detail: str = Field(description="Human-readable explanation")
    status_code: int = Field(description="HTTP status code")


class PaginatedResponse(BaseSchema, Generic[T]):
    """Paginated list response."""

    items: list[T] = Field(description="Page of results")
    total: int = Field(description="Total number of records")
    page: int = Field(ge=1, description="Current page number")
    page_size: int = Field(ge=1, le=200, description="Items per page")
    pages: int = Field(description="Total number of pages")


# ---------------------------------------------------------------------------
# Thought chain
# ---------------------------------------------------------------------------


class ThoughtChainNode(BaseSchema):
    """A single node in the AI's thought chain / reasoning trace."""

    id: UUID = Field(description="Unique node identifier")
    label: str = Field(description="Short human-readable label")
    type: ThoughtType = Field(description="Category of this thought step")
    content: str = Field(description="Full content / reasoning text")
    connections: list[UUID] = Field(
        default_factory=list,
        description="IDs of downstream nodes this node links to",
    )
    created_at: datetime | None = Field(default=None, description="Timestamp when the node was created")


# ---------------------------------------------------------------------------
# Person / Face schemas
# ---------------------------------------------------------------------------


class FaceRegisterRequest(BaseSchema):
    """Register a new face for a named person."""

    name: str = Field(
        min_length=1,
        max_length=128,
        description="Full name of the person to register",
    )
    image: str = Field(
        description="Face image as a base64-encoded data URI or public URL",
    )


class FaceIdentifyRequest(BaseSchema):
    """Identify a person from a face image."""

    image: str = Field(
        description="Face image as a base64-encoded data URI or public URL",
    )
    top_k: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Return up to *top_k* best matches",
    )


class PersonProfileBrief(BaseSchema):
    """Minimal person profile returned alongside face identification."""

    user_id: UUID = Field(description="Unique person / user identifier")
    name: str = Field(description="Display name")
    gender: PersonGender | None = Field(default=None, description="Gender")
    avatar_url: HttpUrl | str | None = Field(default=None, description="Avatar image URL")


class FaceMatchResult(BaseSchema):
    """A single match from face identification."""

    user_id: UUID = Field(description="Matched person identifier")
    name: str = Field(description="Matched person display name")
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Similarity confidence score between 0 and 1",
    )
    profile: PersonProfileBrief | None = Field(default=None, description="Associated person profile (if available)")


class FaceRegisterResponse(BaseSchema):
    """Response after successfully registering a face."""

    user_id: UUID = Field(description="Assigned person / user identifier")
    name: str = Field(description="Registered name")
    face_id: UUID = Field(description="Identifier of the stored face embedding")


# ---------------------------------------------------------------------------
# Chat schemas
# ---------------------------------------------------------------------------


class ChatRequest(BaseSchema):
    """Send a message to the AI digital human."""

    message: str = Field(
        min_length=1,
        description="The user's text message",
    )
    conversation_id: UUID | None = Field(
        default=None,
        description="Continue an existing conversation; omit to start a new one",
    )
    images: list[str] = Field(
        default_factory=list,
        description="Optional list of image URLs or base64 data URIs attached to the message",
    )
    system_prompt_id: UUID | None = Field(
        default=None,
        description="Override the active system prompt for this request",
    )
    stream: bool = Field(
        default=False,
        description="If true, the response will be streamed via SSE",
    )


class ConversationMessage(BaseSchema):
    """A single message within a conversation."""

    id: UUID = Field(description="Message identifier")
    role: str = Field(description="Sender role: 'user' or 'assistant'")
    content: str = Field(description="Message text")
    created_at: datetime = Field(description="When the message was created")


class ChatResponse(BaseSchema):
    """Response from the AI digital human."""

    message: str = Field(description="The assistant's reply text")
    conversation_id: UUID = Field(description="Conversation this reply belongs to")
    user_profile: PersonProfileBrief | None = Field(
        default=None,
        description="Identified user profile (if face recognition was used)",
    )
    thought_chain: list[ThoughtChainNode] = Field(
        default_factory=list,
        description="Optional reasoning trace showing the AI's thought process",
    )
    created_at: datetime | None = Field(default=None, description="Timestamp of the response")


class ConversationListResponse(BaseSchema):
    """Summary of a conversation for listing."""

    id: UUID = Field(description="Conversation identifier")
    title: str | None = Field(default=None, description="Conversation title")
    created_at: datetime = Field(description="When the conversation started")
    updated_at: datetime = Field(description="Last activity timestamp")
    message_count: int = Field(description="Number of messages in the conversation")


# ---------------------------------------------------------------------------
# Multimodal schemas
# ---------------------------------------------------------------------------


class MultimodalAnalyzeRequest(BaseSchema):
    """Submit multimodal content for AI analysis."""

    text: str | None = Field(
        default=None,
        description="Optional text input",
    )
    images: list[str] = Field(
        default_factory=list,
        description="Optional list of image URLs or base64 data URIs",
    )
    audio: str | None = Field(
        default=None,
        description="Optional audio as a base64-encoded data URI",
    )
    video: str | None = Field(
        default=None,
        description="Optional video as a base64-encoded data URI",
    )
    context: str | None = Field(
        default=None,
        description="Free-form context hint to guide analysis",
    )


class MultimodalAnalysisResult(BaseSchema):
    """Result of multimodal content analysis."""

    transcript: str | None = Field(default=None, description="Transcribed text from audio/video")
    description: str | None = Field(default=None, description="Generated description of visual content")
    summary: str = Field(description="Combined analysis summary")
    detected_objects: list[str] = Field(default_factory=list, description="Objects detected in images/video")
    sentiment: str | None = Field(default=None, description="Detected sentiment (positive/negative/neutral)")
    confidence: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Overall confidence of the analysis",
    )


# ---------------------------------------------------------------------------
# Knowledge graph schemas
# ---------------------------------------------------------------------------


class KnowledgeNode(BaseSchema):
    """A single node in the knowledge graph."""

    id: UUID = Field(description="Node identifier")
    label: str = Field(description="Human-readable label")
    type: str = Field(description="Node type, e.g. 'person', 'concept', 'event'")
    properties: dict[str, Any] = Field(default_factory=dict, description="Arbitrary key-value properties")


class KnowledgeEdge(BaseSchema):
    """A directed edge connecting two knowledge-graph nodes."""

    id: UUID = Field(description="Edge identifier")
    source_id: UUID = Field(description="Source node ID")
    target_id: UUID = Field(description="Target node ID")
    relationship: str = Field(description="Relationship type, e.g. 'knows', 'related_to'")
    properties: dict[str, Any] = Field(default_factory=dict, description="Arbitrary key-value properties")


class KnowledgeGraphResponse(BaseSchema):
    """A sub-graph returned from the knowledge store."""

    nodes: list[KnowledgeNode] = Field(description="Nodes in the sub-graph")
    edges: list[KnowledgeEdge] = Field(description="Edges in the sub-graph")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Query metadata such as total count, depth, etc.",
    )


class KnowledgeSearchRequest(BaseSchema):
    """Search the knowledge graph."""

    query: str = Field(min_length=1, description="Natural language search query")
    node_types: list[str] = Field(
        default_factory=list,
        description="Filter results to these node types",
    )
    max_depth: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Max traversal depth from matching nodes",
    )
    limit: int = Field(default=20, ge=1, le=100, description="Maximum number of nodes to return")


# ---------------------------------------------------------------------------
# System prompt schemas
# ---------------------------------------------------------------------------


class SystemPromptCreate(BaseSchema):
    """Create a new system prompt."""

    name: str = Field(
        min_length=1,
        max_length=128,
        description="Short unique name for the prompt",
    )
    content: str = Field(
        min_length=1,
        description="Full system prompt text",
    )
    is_default: bool = Field(
        default=False,
        description="Set as the default system prompt for new conversations",
    )


class SystemPromptUpdate(BaseSchema):
    """Update an existing system prompt."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description="New name for the prompt",
    )
    content: str | None = Field(
        default=None,
        min_length=1,
        description="Updated prompt text",
    )
    is_default: bool | None = Field(
        default=None,
        description="Set or unset as default prompt",
    )


class SystemPromptResponse(BaseSchema):
    """System prompt representation."""

    id: UUID = Field(description="Prompt identifier")
    name: str = Field(description="Prompt name")
    content: str = Field(description="Prompt text")
    is_default: bool = Field(description="Whether this is the default prompt")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last modification timestamp")


# ---------------------------------------------------------------------------
# Speaking style schemas
# ---------------------------------------------------------------------------


class SpeakingStyleCreate(BaseSchema):
    """Create a new speaking style."""

    name: str = Field(
        min_length=1,
        max_length=128,
        description="Short unique name for the style",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional human-readable description",
    )
    style_config: dict[str, Any] = Field(
        description="Style parameters (tone, pace, formality, vocabulary_level, etc.)",
    )
    is_default: bool = Field(
        default=False,
        description="Set as the default speaking style",
    )


class SpeakingStyleUpdate(BaseSchema):
    """Update an existing speaking style."""

    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=128,
        description="New name for the style",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Updated description",
    )
    style_config: dict[str, Any] | None = Field(
        default=None,
        description="Updated style parameters",
    )
    is_default: bool | None = Field(
        default=None,
        description="Set or unset as default style",
    )


class SpeakingStyleResponse(BaseSchema):
    """Speaking style representation."""

    id: UUID = Field(description="Style identifier")
    name: str = Field(description="Style name")
    description: str | None = Field(default=None, description="Style description")
    style_config: dict[str, Any] = Field(description="Style parameters")
    is_default: bool = Field(description="Whether this is the default style")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last modification timestamp")


# ---------------------------------------------------------------------------
# Model configuration schemas
# ---------------------------------------------------------------------------


class ModelConfigUpdate(BaseSchema):
    """Update the active model configuration."""

    llm_model: str | None = Field(
        default=None,
        description="LLM model identifier, e.g. 'openai:gpt-4o'",
    )
    vision_model: str | None = Field(
        default=None,
        description="Vision model identifier, e.g. 'gpt-4o'",
    )
    stt_model: str | None = Field(
        default=None,
        description="Speech-to-text model identifier, e.g. 'turbo'",
    )
    temperature: float | None = Field(
        default=None,
        ge=0.0,
        le=2.0,
        description="LLM sampling temperature",
    )
    max_tokens: int | None = Field(
        default=None,
        ge=1,
        le=32768,
        description="Maximum tokens for LLM responses",
    )


class ModelConfigResponse(BaseSchema):
    """Current model configuration."""

    id: UUID = Field(description="Config record identifier")
    llm_model: str = Field(description="Active LLM model")
    vision_model: str = Field(description="Active vision model")
    stt_model: str = Field(description="Active STT model")
    temperature: float = Field(description="LLM sampling temperature")
    max_tokens: int = Field(description="Maximum response tokens")
    is_active: bool = Field(description="Whether this config is the active one")
    created_at: datetime = Field(description="Creation timestamp")
    updated_at: datetime = Field(description="Last modification timestamp")


# ---------------------------------------------------------------------------
# Person profile schemas
# ---------------------------------------------------------------------------


class PersonProfileUpdate(BaseSchema):
    """Update the AI's profile / memory of a person."""

    appearance_features: dict[str, Any] | None = Field(
        default=None,
        description="Key-value pairs describing appearance (hair color, build, etc.)",
    )
    speaking_style: dict[str, Any] | None = Field(
        default=None,
        description="Key-value pairs describing how the person speaks (tone, pace, etc.)",
    )
    preferences: dict[str, Any] | None = Field(
        default=None,
        description="Known preferences (food, hobbies, communication style, etc.)",
    )
    personality_traits: list[str] | None = Field(
        default=None,
        description="List of personality trait descriptors",
    )
    notes: str | None = Field(
        default=None,
        description="Free-form notes the AI should remember about this person",
    )


class PersonProfileDetail(BaseSchema):
    """Full person profile with all stored metadata."""

    user_id: UUID = Field(description="Unique person identifier")
    name: str = Field(description="Display name")
    gender: PersonGender | None = Field(default=None, description="Gender")
    avatar_url: HttpUrl | str | None = Field(default=None, description="Avatar image URL")
    appearance_features: dict[str, Any] = Field(default_factory=dict)
    speaking_style: dict[str, Any] = Field(default_factory=dict)
    preferences: dict[str, Any] = Field(default_factory=dict)
    personality_traits: list[str] = Field(default_factory=list)
    notes: str | None = Field(default=None, description="Free-form notes")
    face_registered: bool = Field(default=False, description="Whether at least one face is registered")
    created_at: datetime = Field(description="Profile creation timestamp")
    updated_at: datetime = Field(description="Last modification timestamp")


# ---------------------------------------------------------------------------
# Health / misc
# ---------------------------------------------------------------------------


class HealthResponse(BaseSchema):
    """Health-check response."""

    status: str = Field(description="Service status, e.g. 'healthy'")
    version: str = Field(description="API version")
    uptime_seconds: float | None = Field(default=None, description="Process uptime in seconds")
