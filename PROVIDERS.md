# AI Provider 配置指南

本系统支持三种AI provider：GLM、MiniMax和OpenAI。

## 快速配置

### 方案一：使用GLM（智谱AI）

在 `.env` 文件中添加：

```bash
LLM_PROVIDER=glm
VISION_PROVIDER=glm
GLM_API_KEY=你的GLM API密钥
```

GLM模型推荐：

- LLM: `glm-4-flash` (快速/免费), `glm-4` (高质量)
- Vision: `glm-4v-flash`, `glm-4v`

### 方案二：使用MiniMax

在 `.env` 文件中添加：

```bash
LLM_PROVIDER=minimax
MINIMAX_API_KEY=你的MiniMax API密钥
MINIMAX_GROUP_ID=你的Group ID
```

MiniMax模型：

- LLM: `MiniMax-Text-01`
- Vision: `MiniMax-VL-01`

### 方案三：使用OpenAI

在 `.env` 文件中添加：

```bash
LLM_PROVIDER=openai
VISION_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
```

## 获取API密钥

### GLM（智谱AI）

1. 访问 https://open.bigmodel.cn/
2. 注册/登录账号
3. 在控制台创建API Key

### MiniMax

1. 访问 https://api.minimax.chat/
2. 注册/登录账号
3. 获取API Key和Group ID

### OpenAI

1. 访问 https://platform.openai.com/
2. 注册/登录账号
3. 在API Keys页面创建密钥

## 模型对比

| Provider | LLM模型         | Vision模型    | Embedding              | 价格        |
| -------- | --------------- | ------------- | ---------------------- | ----------- |
| GLM      | glm-4-flash     | glm-4v-flash  | embedding-2            | 免费额度    |
| MiniMax  | MiniMax-Text-01 | MiniMax-VL-01 | MiniMax-Embedding-01   | 有免费额度  |
| OpenAI   | gpt-4o          | gpt-4o        | text-embedding-3-small | 按token计费 |

## 人脸识别（必需）

人脸识别使用 InsightFace，无需API Key，完全本地运行。

## 语音转文字（必需）

使用 faster-whisper，完全本地运行，无需API Key。

## 完整配置示例

```bash
# 使用GLM作为主provider
LLM_PROVIDER=glm
VISION_PROVIDER=glm
GLM_API_KEY=xxxxxxxxxxxxx

# 数据库配置
POSTGRES_USER=digitalhuman
POSTGRES_PASSWORD=your-secure-password
DATABASE_URL=postgresql://digitalhuman:your-secure-password@postgres:5432/digitalhuman

# Redis和Qdrant
REDIS_URL=redis://redis:6379/0
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# 人脸识别（默认配置即可）
FACE_RECOGNITION_MODEL=buffalo_l
FACE_SIMILARITY_THRESHOLD=0.65

# Whisper语音识别（默认配置即可）
WHISPER_MODEL_SIZE=turbo
WHISPER_DEVICE=auto
```
