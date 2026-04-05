# AI Digital Human

**Build intelligent digital personas that remember, learn, and evolve.**

A full-stack multimodal AI agent framework that combines conversational AI, vector memory, knowledge graphs, and face recognition into a cohesive digital human experience.

---

## 🇺🇸 English

### The Problem We're Solving

Current AI assistants are **stateless**. Each conversation starts from scratch. They don't remember past interactions, can't recognize familiar faces, and lack persistent understanding of the people they talk to.

**What if an AI could:**
- Remember your preferences across sessions?
- Recognize you by face and know your history?
- Build a growing knowledge graph of everything you've shared?
- Understand context from images, voice, and video — not just text?

### Our Vision

**AI Digital Human** is an open-source framework for building **persistent, multimodal AI personas** that bridge the gap between stateless chatbots and truly intelligent digital companions.

Unlike traditional RAG systems that only retrieve documents, or chatbot frameworks that only handle text, AI Digital Human creates **holistic digital identities** with:

- **Face identity** — Recognize who you're talking to
- **Episodic memory** — Remember conversation history via vector similarity
- **Structured knowledge** — Build knowledge graphs of entities and relationships  
- **Multimodal understanding** — Process images, audio, and video alongside text
- **Configurable personality** — Adjust tone, pace, and speaking style

### Core Architecture

```
User Input (text / image / audio / video)
           │
           ▼
┌──────────────────────────────────────────────────────┐
│              Multimodal Orchestrator                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐│
│  │   Face   │  │   STT    │  │      Vision      ││
│  │Recognition│  │(Whisper) │  │   (GLM-4V/GPT-4V)││
│  └────┬─────┘  └────┬─────┘  └────────┬─────────┘│
│       │              │                   │          │
│       └──────────────┴───────────────────┘          │
│                      │                               │
│                      ▼                               │
│         ┌────────────────────────┐                  │
│         │   Context Assembler    │                  │
│         │  ┌─────────────────┐   │                  │
│         │  │ User Profile    │   │◄── Face ID      │
│         │  │ Vector Memory  │   │◄── Qdrant       │
│         │  │ Knowledge Graph │   │◄── PostgreSQL    │
│         │  │ + System Prompt│   │◄── Speaking Style │
│         │  └─────────────────┘   │                  │
│         └────────────────────────┘                  │
│                      │                               │
│                      ▼                               │
│         ┌────────────────────────┐                  │
│         │    LLM Orchestrator    │                  │
│         │   (GLM-4 / GPT-4o)   │                  │
│         └────────────────────────┘                  │
│                      │                               │
└──────────────────────┼──────────────────────────────┘
                       │
                       ▼
              Streaming Response
```

### Key Systems

#### 1. Memory Architecture (Dual-Store)

| Store | Technology | Purpose | What's Stored |
|-------|------------|---------|--------------|
| **Vector Memory** | Qdrant | Semantic similarity search | Conversation excerpts, facts, preferences |
| **Knowledge Graph** | PostgreSQL | Structured entity relationships | People, concepts, events, connections |

This dual-store approach mirrors how humans use both **associative memory** (similarity-based) and **semantic memory** (structured facts).

#### 2. Face Identity Pipeline

```
Upload Image → InsightFace (ArcFace) → 512-dim Embedding
                                              │
                                              ▼
                                    Qdrant Vector Search
                                              │
                                              ▼
                                    Cosine Similarity > Threshold
                                              │
                                              ▼
                                    User Identity + Profile
```

#### 3. Context Assembly (ChatService)

Before every LLM call, ChatService assembles context from:

1. **Speaking Style** — Tone, pace, formality from database
2. **User Profile** — Name, preferences, appearance from Knowledge Graph
3. **Relevant Memories** — Top-K semantically similar past conversations
4. **Knowledge Subgraph** — Entities and relationships relevant to the query
5. **Multimodal Analysis** — Extracted from images/audio/video inputs

#### 4. Entity Extraction Pipeline

```
Conversation Text
       │
       ▼
LLM (structured output)
       │
       ▼
┌──────────────────────────────────────┐
│  Entities: {name, type, attributes} │
│  Relationships: {source, target,     │
│                 type, strength}     │
└──────────────────────────────────────┘
       │
       ▼
PostgreSQL (Knowledge Graph)
```

### Technical Foundation

This project draws from several research areas:

| Field | Application in This Project |
|-------|---------------------------|
| **Retrieval-Augmented Generation (RAG)** | Vector similarity search for relevant memories |
| **Knowledge Graphs (KG)** | Entity extraction + relationship mapping |
| **Face Recognition** | InsightFace ArcFace embeddings |
| ** Multimodal Learning** | Unified processing of text/image/audio/video |
| **Persona Engineering** | Configurable system prompts + speaking styles |
| **Agent Memory Systems** | Dual-store memory architecture |

### What Makes This Unique

| Aspect | Traditional Chatbot | AI Digital Human |
|--------|-------------------|------------------|
| **Identity** | Anonymous | Face-recognized |
| **Memory** | Session-only | Persistent vector + KG |
| **Context** | Last N messages | Full history + profile |
| **Input** | Text only | Multimodal |
| **Personality** | Fixed | Configurable per-user |
| **Knowledge** | LLM weights | Extracted + structured |

### Quick Start

```bash
# 1. Clone
git clone https://github.com/SonicBotMan/AI-Digital-Human
cd AI-Digital-Human

# 2. Configure
cp .env.default .env
# Edit .env — add your GLM_API_KEY (free at https://open.bigmodel.cn)

# 3. Deploy
./deploy.sh --production

# 4. Access
open http://localhost:3000
```

### Supported Models

| Category | Default | Alternatives |
|----------|---------|--------------|
| **LLM** | GLM-4-Flash (free) | GPT-4o, MiniMax Text-01 |
| **Vision** | GLM-4V-Flash | GPT-4o Vision |
| **STT** | Whisper Turbo | — |
| **Face** | Buffalo_L (ArcFace) | — |

### Tech Stack

**Backend**: FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · PostgreSQL · Qdrant · Redis  
**Frontend**: Next.js 14 · React 18 · TypeScript · Tailwind CSS · shadcn/ui · React Flow  
**AI**: GLM-4 (ZhipuAI) · InsightFace · faster-whisper

### API Highlights

```bash
# Chat with streaming
POST /api/chat/stream  # WebSocket for real-time streaming

# Face identity
POST /api/faces/register  # Register face → embedding stored in Qdrant
POST /api/faces/identify  # Upload image → returns matched user

# Knowledge graph
GET  /api/knowledge/{user_id}/graph      # Full KG as React Flow nodes/edges
POST /api/knowledge/{user_id}/entities   # Add entity
POST /api/knowledge/{user_id}/relationships  # Add relationship

# Multimodal
POST /api/analyze  # Upload image/audio/video → AI analysis + entity extraction
```

Full API docs: `http://localhost:8000/api/docs`

### Development

```bash
# Backend (Python 3.11+)
cd apps/api
source venv/bin/activate
uvicorn app.main:app --reload

# Frontend (Node.js 18+)
cd apps/web
npm install
npm run dev

# Run tests
cd apps/api && pytest tests/
```

### Project Structure

```
apps/
├── api/
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── services/         # Business logic
│   │   │   ├── chat_service.py      # Orchestrates context → LLM
│   │   │   ├── graph_service.py    # Entity extraction + KG CRUD
│   │   │   ├── memory_service.py   # Qdrant vector operations
│   │   │   ├── face_service.py     # InsightFace integration
│   │   │   └── llm_service.py     # LLM abstraction (GLM/GPT)
│   │   ├── routers/          # API endpoints
│   │   ├── models/          # SQLAlchemy + Pydantic schemas
│   │   └── mcp/             # Model Context Protocol server
│   └── tests/               # pytest + httpx
│
└── web/
    ├── src/
    │   ├── app/             # Next.js App Router pages
    │   ├── components/       # React components
    │   │   ├── graph/       # React Flow knowledge graph
    │   │   └── chat/        # Chat UI components
    │   └── hooks/            # Custom React hooks
    └── public/
```

### License

MIT License — see [LICENSE](LICENSE).

---

## 🇨🇳 中文说明

### 我们解决的问题

当前的 AI 助手是**无状态**的。每次对话都从零开始，不记得过去的交互，无法识别人脸，缺乏对对话者的持久理解。

**如果 AI 能够：**
- 跨会话记住你的偏好？
- 通过人脸识别你是谁，并了解你的历史？
- 构建你所分享的一切的知识图谱？
- 理解图像、语音和视频中的上下文——而不仅仅是文本？

### 我们的愿景

**AI Digital Human** 是一个开源框架，用于构建**持久的、多模态的 AI 人格**，弥合无状态聊天机器人与真正智能的数字伴侣之间的差距。

与仅检索文档的传统 RAG 系统，或仅处理文本的聊天机器人框架不同，AI Digital Human 创建**整体数字身份**，具备：

- **人脸身份** — 识别你在和谁说话
- **情景记忆** — 通过向量相似性记住对话历史
- **结构化知识** — 构建实体和关系的知识图谱
- **多模态理解** — 处理图像、音频和视频以及文本
- **可配置人格** — 调整语气、语速和说话风格

### 核心架构

采用双重记忆架构，模拟人类认知：

| 存储 | 技术 | 用途 |
|------|------|------|
| **向量记忆** | Qdrant | 语义相似性搜索 |
| **知识图谱** | PostgreSQL | 结构化实体关系 |

### 快速开始

```bash
# 1. 克隆
git clone https://github.com/SonicBotMan/AI-Digital-Human
cd AI-Digital-Human

# 2. 配置
cp .env.default .env
# 编辑 .env — 添加你的 GLM_API_KEY（在 https://open.bigmodel.cn 免费获取）

# 3. 部署
./deploy.sh --production

# 4. 访问
open http://localhost:3000
```

### 技术栈

**后端**：FastAPI · Pydantic v2 · SQLAlchemy 2.0 (async) · PostgreSQL · Qdrant · Redis  
**前端**：Next.js 14 · React 18 · TypeScript · Tailwind CSS · shadcn/ui · React Flow  
**AI**：GLM-4 (智谱AI) · InsightFace · faster-whisper

### 许可证

MIT License — 见 [LICENSE](LICENSE)。

---

<p align="center">
  <strong>Star ⭐ if you find this interesting — contributions welcome!</strong>
</p>
