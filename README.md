# AI Digital Human - 数字人智能系统

基于多模态AI的数字人产品，支持人脸识别、记忆系统、知识图谱可视化。

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

## 🚀 快速开始

### 前置条件

- Docker & Docker Compose
- Node.js 18+ (本地开发)
- Python 3.11+ (本地开发)

### 使用Docker启动（推荐）

```bash
# 1. 进入项目目录
cd "Agent Talk"

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 OPENAI_API_KEY

# 3. 启动所有服务
docker compose up -d

# 4. 访问应用
# 前端: http://localhost:3000
# API:  http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 本地开发

```bash
# 后端
cd apps/api
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# 前端
cd apps/web
npm install
npm run dev  # 启动在 :3000
```

## ⚙️ 环境变量

| 变量                        | 说明            | 默认值                     |
| --------------------------- | --------------- | -------------------------- |
| `OPENAI_API_KEY`            | OpenAI API密钥  | **必需**                   |
| `DEFAULT_LLM_MODEL`         | 默认LLM模型     | `openai:gpt-4o`            |
| `VISION_MODEL`              | 视觉模型        | `gpt-4o`                   |
| `WHISPER_MODEL_SIZE`        | Whisper模型大小 | `turbo`                    |
| `FACE_RECOGNITION_MODEL`    | 人脸识别模型    | `buffalo_l`                |
| `FACE_SIMILARITY_THRESHOLD` | 人脸匹配阈值    | `0.65`                     |
| `POSTGRES_URL`              | PostgreSQL连接  | `postgresql+asyncpg://...` |
| `REDIS_URL`                 | Redis连接       | `redis://redis:6379/0`     |
| `QDRANT_HOST`               | Qdrant地址      | `qdrant`                   |
| `QDRANT_PORT`               | Qdrant端口      | `6333`                     |

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
