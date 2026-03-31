"""SQLAlchemy 2.0 async ORM models. PostgreSQL 16 + asyncpg."""

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    Uuid,
)
from sqlalchemy import JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {
        dict: JSON,
    }


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


# User


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    person_profile: Mapped["PersonProfile | None"] = relationship(
        "PersonProfile",
        back_populates="user",
        uselist=False,
        lazy="selectin",
    )
    conversations: Mapped[list["Conversation"]] = relationship(
        "Conversation",
        back_populates="user",
        lazy="selectin",
    )
    knowledge_entities: Mapped[list["KnowledgeEntity"]] = relationship(
        "KnowledgeEntity",
        back_populates="user",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id!s} name={self.name!r} email={self.email!r}>"


# PersonProfile


class PersonProfile(Base):
    __tablename__ = "person_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    appearance_features: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    speaking_style: Mapped[str | None] = mapped_column(Text, nullable=True)
    preferences: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    personality_traits: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    user: Mapped["User"] = relationship("User", back_populates="person_profile")

    def __repr__(self) -> str:
        return f"<PersonProfile id={self.id!s} user_id={self.user_id!s}>"


# Conversation


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="conversations")
    messages: Mapped[list["Message"]] = relationship(
        "Message",
        back_populates="conversation",
        order_by="Message.created_at",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Conversation id={self.id!s} title={self.title!r}>"


# Message


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata",
        JSON,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (Index("ix_messages_conversation_created", "conversation_id", "created_at"),)

    conversation: Mapped["Conversation"] = relationship(
        "Conversation",
        back_populates="messages",
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id!s} role={self.role!r} conversation_id={self.conversation_id!s}>"


# SystemPrompt


class SystemPrompt(TimestampMixin, Base):
    __tablename__ = "system_prompts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SystemPrompt id={self.id!s} name={self.name!r} default={self.is_default}>"


# SpeakingStyle


class SpeakingStyle(TimestampMixin, Base):
    __tablename__ = "speaking_styles"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)
    style_config: Mapped[dict] = mapped_column(JSON, nullable=False)
    is_default: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<SpeakingStyle id={self.id!s} name={self.name!r} default={self.is_default}>"


# ModelConfig


class ModelConfig(TimestampMixin, Base):
    __tablename__ = "model_configs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    llm_model: Mapped[str] = mapped_column(String(255), nullable=False)
    vision_model: Mapped[str] = mapped_column(String(255), nullable=False)
    stt_model: Mapped[str] = mapped_column(String(255), nullable=False)
    temperature: Mapped[float] = mapped_column(nullable=False, default=0.7)
    max_tokens: Mapped[int] = mapped_column(nullable=False, default=4096)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<ModelConfig id={self.id!s} llm={self.llm_model!r} active={self.is_active}>"


# KnowledgeEntity


class KnowledgeEntity(Base):
    __tablename__ = "knowledge_entities"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (Index("ix_knowledge_entities_user_type", "user_id", "entity_type"),)

    user: Mapped["User"] = relationship("User", back_populates="knowledge_entities")
    source_relationships: Mapped[list["KnowledgeRelationship"]] = relationship(
        "KnowledgeRelationship",
        back_populates="source_entity",
        foreign_keys="KnowledgeRelationship.source_entity_id",
        lazy="selectin",
    )
    target_relationships: Mapped[list["KnowledgeRelationship"]] = relationship(
        "KnowledgeRelationship",
        back_populates="target_entity",
        foreign_keys="KnowledgeRelationship.target_entity_id",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<KnowledgeEntity id={self.id!s} type={self.entity_type!r} name={self.name!r}>"


# KnowledgeRelationship


class KnowledgeRelationship(Base):
    __tablename__ = "knowledge_relationships"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4,
    )
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("knowledge_entities.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    relationship_type: Mapped[str] = mapped_column(String(100), nullable=False)
    strength: Mapped[float] = mapped_column(nullable=False, default=1.0)
    attributes: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index(
            "ix_knowledge_rel_source_type",
            "source_entity_id",
            "relationship_type",
        ),
        Index(
            "ix_knowledge_rel_unique_pair",
            "source_entity_id",
            "target_entity_id",
            "relationship_type",
            unique=True,
        ),
    )

    source_entity: Mapped["KnowledgeEntity"] = relationship(
        "KnowledgeEntity",
        back_populates="source_relationships",
        foreign_keys=[source_entity_id],
    )
    target_entity: Mapped["KnowledgeEntity"] = relationship(
        "KnowledgeEntity",
        back_populates="target_relationships",
        foreign_keys=[target_entity_id],
    )

    def __repr__(self) -> str:
        return (
            f"<KnowledgeRelationship id={self.id!s} "
            f"type={self.relationship_type!r} "
            f"source={self.source_entity_id!s} -> target={self.target_entity_id!s}>"
        )
