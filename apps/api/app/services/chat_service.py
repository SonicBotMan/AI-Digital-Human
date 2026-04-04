"""Chat Engine Service — orchestrates conversation flow, context assembly, and post-response processing.

Coordinates LLMService, MemoryService, GraphService, and MultimodalService
to deliver rich, context-aware chat interactions for the AI Digital Human.
"""

from __future__ import annotations

import logging
import uuid
from collections.abc import AsyncIterator
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.models.database import Conversation, Message
from app.services.graph_service import GraphService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default configuration values
# ---------------------------------------------------------------------------

DEFAULT_SYSTEM_PROMPT = (
    "You are an intelligent, empathetic AI digital human assistant. "
    "You remember details about the people you talk to and build "
    "relationships over time. Be warm, helpful, and natural in conversation."
)

MAX_CONTEXT_LENGTH: int = 8000
MEMORY_SEARCH_LIMIT: int = 5
CONVERSATION_HISTORY_LIMIT: int = 50


class ChatServiceError(Exception):
    """Raised when a chat operation fails."""


class ChatService:
    """Main orchestrator for chat interactions.

    Assembles context from multiple sources (user profile, memories,
    knowledge graph, multimodal analysis, conversation history) and
    delegates LLM completion to ``LLMService``. After each response,
    extracts entities, stores memories, and updates the user profile.

    Parameters
    ----------
    db_session:
        SQLAlchemy ``AsyncSession`` for relational data.
    llm_service:
        Service for LLM completions and embeddings.
    memory_service:
        Service for vector-based memory storage and retrieval.
    graph_service:
        Service for knowledge-graph entity/relationship management.
    settings:
        Application settings instance.
    """

    def __init__(
        self,
        db_session: AsyncSession,
        llm_service: LLMService,
        memory_service: MemoryService,
        graph_service: GraphService,
        settings: Settings,
    ) -> None:
        self._db = db_session
        self._llm = llm_service
        self._memory = memory_service
        self._graph = graph_service
        self._settings = settings

        self._system_prompt = getattr(settings, "DEFAULT_SYSTEM_PROMPT", None) or DEFAULT_SYSTEM_PROMPT
        self._max_context_length: int = getattr(settings, "MAX_CONTEXT_LENGTH", None) or MAX_CONTEXT_LENGTH
        self._memory_search_limit: int = getattr(settings, "MEMORY_SEARCH_LIMIT", None) or MEMORY_SEARCH_LIMIT
        self._history_limit: int = getattr(settings, "CONVERSATION_HISTORY_LIMIT", None) or CONVERSATION_HISTORY_LIMIT
        self._style_directive: str | None = None

        logger.info(
            "ChatService initialised — max_context=%d memory_limit=%d",
            self._max_context_length,
            self._memory_search_limit,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def chat(
        self,
        user_id: str | uuid.UUID,
        message: str,
        conversation_id: str | uuid.UUID | None = None,
        multimodal_context: dict[str, Any] | None = None,
        *,
        system_prompt_override: str | None = None,
    ) -> dict[str, Any]:
        """Main chat flow: assemble context → LLM call → post-processing.

        Parameters
        ----------
        user_id:
            The user initiating the conversation.
        message:
            The user's text message.
        conversation_id:
            Optional existing conversation to continue.  If *None*, a new
            conversation is created automatically.
        multimodal_context:
            Optional output from ``MultimodalService.process_input``.
        system_prompt_override:
            Optional per-request system prompt override.

        Returns
        -------
        dict
            ``{"conversation_id", "message_id", "response", "entities_extracted"}``
        """
        user_uuid = self._to_uuid(user_id)

        if conversation_id is not None:
            conv_uuid = self._to_uuid(conversation_id)
            conversation = await self._db.get(Conversation, conv_uuid)
            if conversation is None:
                raise ChatServiceError(f"Conversation {conversation_id} not found")
        else:
            conv_uuid = await self.create_conversation(user_uuid)
            conversation = await self._db.get(Conversation, conv_uuid)

        user_msg = Message(
            conversation_id=conv_uuid,
            role="user",
            content=message,
            metadata_=multimodal_context,
        )
        self._db.add(user_msg)
        await self._db.flush()

        context_str = await self._build_context(user_uuid, message, multimodal_context)
        history = await self.get_conversation_history(conv_uuid, limit=self._history_limit)

        llm_messages: list[dict[str, str]] = []
        for msg in history[:-1]:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        if not llm_messages or llm_messages[-1]["role"] != "user":
            llm_messages.append({"role": "user", "content": message})

        effective_system_prompt = system_prompt_override or self._system_prompt
        enriched_system = f"{effective_system_prompt}\n\n{context_str}" if context_str else effective_system_prompt
        enriched_system = self._truncate(enriched_system, self._max_context_length)

        response_text = self._llm.chat_completion(
            messages=llm_messages,
            system_prompt=enriched_system,
        )

        assistant_msg = Message(
            conversation_id=conv_uuid,
            role="assistant",
            content=response_text,
        )
        self._db.add(assistant_msg)
        await self._db.flush()
        await self._db.commit()

        entities_extracted: list[dict[str, Any]] = []
        try:
            entities_extracted = await self._post_process(user_uuid, message, response_text)
        except Exception:
            logger.warning("Post-processing failed for conversation %s", conv_uuid, exc_info=True)

        return {
            "conversation_id": str(conv_uuid),
            "message_id": str(assistant_msg.id),
            "response": response_text,
            "entities_extracted": entities_extracted,
        }

    async def stream_chat(
        self,
        user_id: str | uuid.UUID,
        message: str,
        conversation_id: str | uuid.UUID | None = None,
        multimodal_context: dict[str, Any] | None = None,
        *,
        system_prompt_override: str | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        user_uuid = self._to_uuid(user_id)

        if conversation_id is not None:
            conv_uuid = self._to_uuid(conversation_id)
            conversation = await self._db.get(Conversation, conv_uuid)
            if conversation is None:
                raise ChatServiceError(f"Conversation {conversation_id} not found")
        else:
            conv_uuid = await self.create_conversation(user_uuid)
            conversation = await self._db.get(Conversation, conv_uuid)

        user_msg = Message(
            conversation_id=conv_uuid,
            role="user",
            content=message,
            metadata_=multimodal_context,
        )
        self._db.add(user_msg)
        await self._db.flush()

        context_str = await self._build_context(user_uuid, message, multimodal_context)
        history = await self.get_conversation_history(conv_uuid, limit=self._history_limit)

        llm_messages: list[dict[str, str]] = []
        for msg in history[:-1]:
            llm_messages.append({"role": msg["role"], "content": msg["content"]})

        if not llm_messages or llm_messages[-1]["role"] != "user":
            llm_messages.append({"role": "user", "content": message})

        effective_system_prompt = system_prompt_override or self._system_prompt
        enriched_system = f"{effective_system_prompt}\n\n{context_str}" if context_str else effective_system_prompt
        enriched_system = self._truncate(enriched_system, self._max_context_length)

        collected_tokens: list[str] = []
        async for token in self._llm.stream_chat_completion(
            messages=llm_messages,
            system_prompt=enriched_system,
        ):
            collected_tokens.append(token)
            yield {"type": "token", "content": token}

        response_text = "".join(collected_tokens)

        assistant_msg = Message(
            conversation_id=conv_uuid,
            role="assistant",
            content=response_text,
        )
        self._db.add(assistant_msg)
        await self._db.flush()
        await self._db.commit()

        try:
            await self._post_process(user_uuid, message, response_text)
        except Exception:
            logger.warning("Post-processing failed for conversation %s", conv_uuid, exc_info=True)

        yield {
            "type": "end",
            "conversation_id": str(conv_uuid),
            "message_id": str(assistant_msg.id),
        }

    async def get_conversation_history(
        self,
        conversation_id: str | uuid.UUID,
        limit: int = CONVERSATION_HISTORY_LIMIT,
    ) -> list[dict[str, Any]]:
        """Retrieve message history for a conversation, ordered chronologically.

        Parameters
        ----------
        conversation_id:
            The conversation to fetch.
        limit:
            Maximum number of messages to return (default 50).

        Returns
        -------
        list[dict]
            Each dict has keys ``id, role, content, metadata, created_at``.
        """
        conv_uuid = self._to_uuid(conversation_id)

        stmt = (
            select(Message).where(Message.conversation_id == conv_uuid).order_by(Message.created_at.asc()).limit(limit)
        )
        result = await self._db.execute(stmt)
        messages = result.scalars().all()

        return [
            {
                "id": str(msg.id),
                "role": msg.role,
                "content": msg.content,
                "metadata": msg.metadata_,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
            }
            for msg in messages
        ]

    async def create_conversation(
        self,
        user_id: str | uuid.UUID,
        title: str | None = None,
    ) -> uuid.UUID:
        """Create a new conversation and return its UUID.

        Parameters
        ----------
        user_id:
            Owner of the conversation.
        title:
            Optional human-readable title.

        Returns
        -------
        uuid.UUID
            The ID of the newly created conversation.
        """
        user_uuid = self._to_uuid(user_id)
        conversation = Conversation(
            user_id=user_uuid,
            title=title,
        )
        self._db.add(conversation)
        await self._db.flush()
        await self._db.commit()

        logger.info("Created conversation %s for user %s", conversation.id, user_uuid)
        return conversation.id

    async def list_conversations(
        self,
        user_id: str | uuid.UUID,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict[str, Any]], int]:
        user_uuid = self._to_uuid(user_id)
        offset = (page - 1) * page_size

        from sqlalchemy import func, select

        count_stmt = select(func.count(Conversation.id)).where(Conversation.user_id == user_uuid)
        count_result = await self._db.execute(count_stmt)
        total = count_result.scalar() or 0

        stmt = (
            select(Conversation)
            .where(Conversation.user_id == user_uuid)
            .order_by(Conversation.updated_at.desc())
            .offset(offset)
            .limit(page_size)
        )
        result = await self._db.execute(stmt)
        conversations = result.scalars().all()

        items = []
        for conv in conversations:
            msg_count_stmt = select(func.count(Message.id)).where(Message.conversation_id == conv.id)
            msg_count_result = await self._db.execute(msg_count_stmt)
            msg_count = msg_count_result.scalar() or 0

            items.append(
                {
                    "id": str(conv.id),
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat() if conv.created_at else None,
                    "updated_at": conv.updated_at.isoformat() if conv.updated_at else None,
                    "message_count": msg_count,
                }
            )

        return items, total

    # ------------------------------------------------------------------
    # Context Assembly
    # ------------------------------------------------------------------

    async def _ensure_style_directive(self) -> str:
        from sqlalchemy import select
        from app.models.database import SpeakingStyle

        style_id = getattr(self._settings, "DEFAULT_SPEAKING_STYLE_ID", None)
        if style_id is None:
            stmt = select(SpeakingStyle).where(SpeakingStyle.is_default == True).limit(1)
        else:
            stmt = select(SpeakingStyle).where(SpeakingStyle.id == style_id).limit(1)

        result = await self._db.execute(stmt)
        style = result.scalar_one_or_none()

        if style is None:
            self._style_directive = ""
            return ""

        cfg = style.style_config or {}
        parts = []
        if tone := cfg.get("tone"):
            parts.append(f"- Tone: {tone}")
        if pace := cfg.get("pace"):
            parts.append(f"- Pace: {pace}")
        if formality := cfg.get("formality"):
            parts.append(f"- Formality: {formality}")
        if vocab := cfg.get("vocabulary_level"):
            parts.append(f"- Vocabulary: {vocab}")
        if cfg.get("use_emoji"):
            parts.append("- You may use emoji")
        if not cfg.get("humor_allowed", True):
            parts.append("- Avoid humor")

        if parts:
            self._style_directive = "\n[Speaking Style]\n" + "\n".join(parts)
        else:
            self._style_directive = ""

        return self._style_directive

    async def _build_context(
        self,
        user_id: uuid.UUID,
        message: str,
        multimodal_context: dict[str, Any] | None,
    ) -> str:
        """Assemble rich context string from all available sources.

        Sources (in order of assembly):
        1. User profile (from knowledge graph via ``GraphService.build_user_profile``)
        2. Relevant memories (vector search via ``MemoryService.search_memories``)
        3. Knowledge subgraph (entities + relationships)
        4. Multimodal analysis (if provided)
        5. Conversation history (handled separately in ``chat()``)

        Returns
        -------
        str
            Newline-separated context block for the system prompt.
        """
        parts: list[str] = []

        style_directive = await self._ensure_style_directive()
        if style_directive:
            parts.append(style_directive)

        try:
            profile = await self._graph.build_user_profile(user_id)
            if profile and profile.get("summary"):
                parts.append(f"[User Profile]\n{profile['summary']}")
                categories = profile.get("categories", {})
                for entity_type, entries in categories.items():
                    for entry in entries[:10]:
                        rels = entry.get("relationships", [])
                        rel_strs = [
                            f"{r['type']} {r['target']} ({r['direction']}, strength={r['strength']})" for r in rels[:5]
                        ]
                        line = f"- {entry['name']} ({entity_type})"
                        if rel_strs:
                            line += f" | {', '.join(rel_strs)}"
                        parts.append(line)
        except Exception:
            logger.debug("User profile assembly failed", exc_info=True)

        try:
            message_embedding = self._llm.embed_text(message)
            memories = self._memory.search_memories(
                user_id=str(user_id),
                query_embedding=message_embedding,
                limit=self._memory_search_limit,
            )
            if memories:
                memory_lines = [f"- [{m.get('score', 0):.2f}] {m['content']}" for m in memories]
                parts.append("[Relevant Memories]\n" + "\n".join(memory_lines))
        except Exception:
            logger.debug("Memory search failed", exc_info=True)

        try:
            subgraph = await self._graph.get_user_subgraph(user_id, depth=2)
            nodes = subgraph.get("nodes", [])
            edges = subgraph.get("edges", [])
            if nodes:
                node_strs = [f"  {n['label']} ({n['type']})" for n in nodes[:20]]
                parts.append("[Knowledge Entities]\n" + "\n".join(node_strs))
            if edges:
                edge_strs = [f"  {e['source']} --[{e['type']}]--> {e['target']}" for e in edges[:20]]
                parts.append("[Knowledge Relationships]\n" + "\n".join(edge_strs))
        except Exception:
            logger.debug("Subgraph assembly failed", exc_info=True)

        if multimodal_context:
            mm_parts: list[str] = []

            text_content = multimodal_context.get("text_content")
            if text_content:
                mm_parts.append(f"Transcribed text: {text_content}")

            visual_analyses = multimodal_context.get("visual_analysis", [])
            if visual_analyses:
                for i, analysis in enumerate(visual_analyses[:3]):
                    description = analysis.get("description", str(analysis))
                    mm_parts.append(f"Visual analysis [{i + 1}]: {description}")

            face_matches = multimodal_context.get("face_matches", [])
            if face_matches:
                for match in face_matches:
                    name = match.get("name", "unknown")
                    score = match.get("score", 0)
                    mm_parts.append(f"Recognised face: {name} (confidence: {score})")

            audio_transcript = multimodal_context.get("audio_transcript")
            if audio_transcript and audio_transcript.get("text"):
                mm_parts.append(f"Audio transcript: {audio_transcript['text']}")

            if mm_parts:
                parts.append("[Multimodal Context]\n" + "\n".join(mm_parts))

        full_context = "\n\n".join(parts)
        return self._truncate(full_context, self._max_context_length)

    # ------------------------------------------------------------------
    # Post-Processing
    # ------------------------------------------------------------------

    async def _post_process(
        self,
        user_id: uuid.UUID,
        user_message: str,
        assistant_response: str,
    ) -> list[dict[str, Any]]:
        """Extract entities from the exchange and store as memories.

        Steps:
        1. Extract entities/relationships via ``GraphService``.
        2. Store the exchange as a vector memory via ``MemoryService``.
        3. Update the user profile in the vector store.

        Returns
        -------
        list[dict]
            Entities and relationships extracted from the conversation.
        """
        combined_text = f"User: {user_message}\nAssistant: {assistant_response}"

        extracted = await self._graph.extract_entities_from_text(combined_text, user_id)

        try:
            memory_text = f"User said: {user_message}"
            embedding = self._llm.embed_text(memory_text)
            self._memory.store_memory(
                user_id=str(user_id),
                content=memory_text,
                embedding=embedding,
                metadata={
                    "conversation_type": "chat",
                    "response_preview": assistant_response[:200],
                },
            )
        except Exception:
            logger.debug("Memory storage failed", exc_info=True)

        try:
            profile = await self._graph.build_user_profile(user_id)
            if profile:
                self._memory.update_user_profile(
                    user_id=str(user_id),
                    data={
                        "knowledge_summary": profile.get("summary", ""),
                        "entity_count": profile.get("entity_count", 0),
                    },
                )
        except Exception:
            logger.debug("Profile update failed", exc_info=True)

        return extracted

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_uuid(value: str | uuid.UUID) -> uuid.UUID:
        """Normalise a string or UUID to ``uuid.UUID``."""
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except ValueError as exc:
            raise ChatServiceError(f"Invalid UUID: {value}") from exc

    @staticmethod
    def _truncate(text: str, max_length: int) -> str:
        """Truncate *text* to *max_length* characters, preserving word boundaries."""
        if len(text) <= max_length:
            return text
        truncated = text[:max_length]
        for sep in ("\n", " "):
            idx = truncated.rfind(sep)
            if idx > max_length * 0.8:
                truncated = truncated[:idx]
                break
        return truncated + "\n[...truncated]"
