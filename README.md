# AI Digital Human - Zero-Configuration Digital Human System

Multimodal AI digital human with face recognition, memory system, and knowledge graph visualization.

---

## 🇺🇸 English | [🇨🇳 中文](#中文说明)

### ✨ Features

| Feature | Description |
|---------|-------------|
| **Zero-Config** | Works out-of-the-box with GLM/MiniMax models |
| **Low Memory** | Runs smoothly on servers with 4GB RAM |
| **MCP Protocol** | Model Context Protocol support for extensibility |
| **One-Click Deploy** | `./deploy.sh` for zero-configuration startup |

### 🎯 Core Capabilities

- **Multimodal Input**: Images, text, video, and audio file uploads
- **Face Recognition**: InsightFace ArcFace model, 99.77% LFW accuracy
- **Memory System**: Qdrant vector database for semantic conversation search
- **Knowledge Graph**: Structured storage of person attributes, preferences, and relationships
- **Visual Thinking Network**: React Flow for thought chain visualization
- **AI Chat**: GPT-4o-powered intelligent conversation with streaming responses
- **Admin Dashboard**: System prompts, speaking styles, and model configuration

### 🚀 Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/SonicBotMan/ai-digital-human
cd AI-Digital-Human

# 2. Configure API keys
cp .env.default .env
# Edit .env and add your GLM_API_KEY

# 3. One-click deployment
./deploy.sh --production

# 4. Access the app
# Frontend: http://localhost:3000
# API: http://localhost:8000
# API Docs: http://localhost:8000/api/docs
```

### 📄 License

MIT License - See [LICENSE](LICENSE) file.

---

## 🇨🇳 中文说明

## ✨ 新特性

| 特性                      | 说明                          |
| ------------------------- | ----------------------------- |
| **开箱即用**              | GLM/MiniMax 模型，开源免费用   |
| **低内存优化**            | 4GB 服务器轻松运行             |
| **MCP Protocol 支持**     | 模型上下文协议，扩展性强        |
| **一键部署**              | `./deploy.sh` 零配置启动       |

## 🎯 核心功能

| 功能             | 说明                                    |
| ---------------- | --------------------------------------- |
| **多模态输入**   | 支持图片、文字、视频、音频文件上传      |
| **人脸识别**     | InsightFace ArcFace模型，LFW 99.77%精度 |
| **记忆系统**     | Qdrant向量数据库，语义检索历史对话      |
| **知识图谱**     | 人物特征、偏好、关系的结构化存储        |
| **可视化思维网** | React Flow展示思维链路和信息脉络        |
| **AI对话**       | GPT-4o驱动的智能对话，支持流式响应      |
| **后台管理**     | 系统提示词、说话风格、模型配置          |

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端 (Next.js :3000)                  │
│  ┌─────────┐ ┌───────────────┐ ┌─────────┐ ┌────────┐  │
│  │ Chat UI │ │ Knowledge Graph│ │  Admin  │ │ API Docs│  │
│  └────┬────┘ └───────┬───────┘ └────┬────┘ └───┬────┘  │
│       └──────────────┴──────────────┴──────────┘        │
│                         REST + WebSocket                 │
└─────────────────────────────┬───────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────┐
│                  API网关 (FastAPI :8000)                 │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────┐   │
│  │  Chat   │ │  Face   │ │Knowledge│ │ Multimodal  │   │
│  │ Service │ │ Service │ │ Service │ │ Orchestrator│   │
│  └────┬────┘ └────┬────┘ └────┬────┘ └──────┬──────┘   │
│       └───────────┴───────────┴─────────────┘           │
│              AI服务层: LLM, Vision, STT, Face           │
└─────────────────────────────┬───────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────┐
│                       数据层                             │
│  ┌──────────┐  ┌──────────┐  ┌───────┐  ┌──────────┐   │
│  │PostgreSQL│  │ Qdrant   │  │ Redis │  │   Files  │   │
│  │用户/会话 │  │向量存储  │  │ 缓存  │  │ 图片/音频│   │
│  └──────────┘  └──────────┘  └───────┘  └──────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 🚀 快速开始 (开箱即用)

### 前置条件
- Docker & Docker Compose
- GLM API Key (从 https://open.bigmodel.cn/ 获取)

### 一键部署 (推荐)

```bash
# 1. 克隆项目
git clone <repo-url>
cd "Agent Talk"

# 2. 配置API密钥
cp .env.default .env
# 编辑 .env，填入你的 GLM_API_KEY

# 3. 一键部署
./deploy.sh --production

# 4. 访问应用
# 前端: http://localhost:3000
# API:  http://localhost:8000
# API文档: http://localhost:8000/api/docs
```

### 开发模式

```bash
# 使用 docker-compose.yml (需要 PostgreSQL + Qdrant)
docker compose up -d

# 或使用 Makefile
make dev
```

## ⚙️ 环境变量

| 变量                        | 说明              | 默认值                     |
| --------------------------- | ----------------- | -------------------------- |
| `GLM_API_KEY`               | 智谱GLM API密钥   | **必需** (开箱即用)        |
| `MINIMAX_API_KEY`           | MiniMax API密钥   | 可选                       |
| `OPENAI_API_KEY`            | OpenAI API密钥    | 可选                       |
| `DEFAULT_LLM_MODEL`         | 默认LLM模型       | `glm-4-flash`             |
| `VISION_MODEL`              | 视觉模型          | `glm-4v-flash`            |
| `WHISPER_MODEL_SIZE`        | Whisper模型大小   | `turbo`                   |
| `FACE_RECOGNITION_MODEL`    | 人脸识别模型      | `buffalo_l`               |
| `FACE_SIMILARITY_THRESHOLD` | 人脸匹配阈值      | `0.65`                    |
| `POSTGRES_URL`              | PostgreSQL连接    | `postgresql+asyncpg://...`|
| `REDIS_URL`                 | Redis连接         | `redis://redis:6379/0`    |
| `QDRANT_HOST`               | Qdrant地址        | `qdrant`                  |
| `QDRANT_PORT`               | Qdrant端口        | `6333`                    |

完整配置见 `.env.example`

## 📡 API接口

| 方法   | 路径                         | 说明               |
| ------ | ---------------------------- | ------------------ |
| `POST` | `/chat`                      | 发送消息，获取回复 |
| `WS`   | `/chat/stream`               | WebSocket流式对话  |
| `POST` | `/faces/register`            | 注册人脸           |
| `POST` | `/faces/identify`            | 识别用户           |
| `POST` | `/analyze`                   | 多模态输入分析     |
| `GET`  | `/knowledge/{user_id}/graph` | 获取知识图谱       |
| `GET`  | `/admin/prompts`             | 管理系统提示词     |
| `GET`  | `/admin/styles`              | 管理说话风格       |
| `GET`  | `/admin/models`              | 管理模型配置       |

完整API文档: http://localhost:8000/docs

## 📁 项目结构

```
Agent Talk/
├── apps/
│   ├── api/                    # Python FastAPI后端
│   │   ├── app/
│   │   │   ├── main.py         # 应用入口
│   │   │   ├── core/           # 配置、安全
│   │   │   ├── models/         # 数据库模型、Schemas
│   │   │   ├── routers/        # API路由
│   │   │   ├── services/       # 业务逻辑服务
│   │   │   └── db/             # 数据库会话、迁移
│   │   └── tests/              # 后端测试
│   │
│   └── web/                    # Next.js前端
│       ├── src/
│       │   ├── app/            # 页面路由
│       │   ├── components/     # React组件
│       │   ├── hooks/          # 自定义Hooks
│       │   └── lib/            # 工具函数
│       └── tests/              # 前端测试
│
├── docker-compose.yml          # 开发环境
├── docker-compose.test.yml     # 测试环境
├── turbo.json                  # Turborepo配置
└── README.md                   # 本文件
```

## 💾 内存优化说明

默认配置针对 4GB 内存服务器优化:
- 使用 SQLite 替代 PostgreSQL (节省 ~300MB)
- 使用 Qdrant Local Mode (节省 ~300MB)
- Redis 内存限制 200MB
- 总内存占用 ~1.2-1.5GB

## 🤖 支持的模型

默认启用 (开箱即用):
- LLM: GLM-4-Flash, GLM-4
- Vision: GLM-4V-Flash
- STT: Whisper Turbo

可选配置:
- MiniMax Text-01
- OpenAI GPT-4o

## 🛠️ 技术栈

### 后端

- **框架**: FastAPI + Pydantic v2
- **数据库**: PostgreSQL 16 + SQLAlchemy 2.0 (async)
- **向量存储**: Qdrant
- **缓存**: Redis 7
- **AI模型**: OpenAI GPT-4o, InsightFace, faster-whisper

### 前端

- **框架**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + shadcn/ui
- **图谱可视化**: React Flow + D3-force
- **状态管理**: React Hooks
- **HTTP**: Fetch API + WebSocket

## 🐛 常见问题

### Q: 启动时报错 "OPENAI_API_KEY is required"

A: 在 `.env` 文件中添加你的OpenAI API密钥

### Q: 人脸识别不工作

A: 确保已安装 InsightFace 依赖：`pip install insightface onnxruntime`

### Q: 知识图谱显示空白

A: 需要先通过 `/faces/register` 注册用户，或通过 `/analyze` 上传图片触发自动识别

### Q: WebSocket连接失败

A: 检查后端是否在 :8000 端口运行，且防火墙允许连接

## 📄 许可证

MIT License
