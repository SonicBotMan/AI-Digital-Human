from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Project ---
    PROJECT_NAME: str = "AI Digital Human"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # --- Database ---
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/digital_human"

    # --- Redis ---
    REDIS_URL: str = "redis://localhost:6379/0"

    # --- Qdrant ---
    QDRANT_MODE: str = "local"  # "local" or "server"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    QDRANT_GRPC_PORT: int = 6334
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION: str = "face_embeddings"
    MEMORY_EMBEDDING_DIM: int = 1024

    # --- LLM Provider Selection (openai/glm/minimax) ---
    LLM_PROVIDER: str = "glm"

    # --- GLM (智谱AI) ---
    GLM_API_KEY: str = ""
    GLM_MODEL: str = "glm-4-flash"

    # --- MiniMax ---
    MINIMAX_API_KEY: str = ""
    MINIMAX_GROUP_ID: str = ""
    MINIMAX_MODEL: str = "MiniMax-Text-01"

    # --- OpenAI ---
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"

    # --- LLM通用配置 ---
    DEFAULT_LLM_MODEL: str = "glm-4-flash"
    MAX_TOKENS: int = 4096
    TEMPERATURE: float = 0.7

    # --- Vision ---
    VISION_PROVIDER: str = "glm"
    VISION_MODEL: str = "glm-4v-flash"
    VISION_MAX_TOKENS: int = 1000

    # --- InsightFace / Face Recognition ---
    INSIGHTFACE_MODEL_ROOT: str = "./models"
    FACE_RECOGNITION_MODEL: str = "buffalo_l"
    FACE_SIMILARITY_THRESHOLD: float = 0.65
    FACE_EMBEDDING_DIM: int = 512

    # --- Whisper (faster-whisper) ---
    WHISPER_MODEL_SIZE: str = "turbo"
    WHISPER_DEVICE: str = "auto"
    WHISPER_COMPUTE_TYPE: str = "float16"

    # --- CORS ---
    CORS_ORIGINS: list[str] = ["https://wen.pmparker.net"]

    # --- JWT Auth ---
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD: str = "change-me-in-production"


settings = Settings()
