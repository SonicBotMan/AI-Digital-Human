from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.chat import router as chat_router
from app.routers.faces import router as faces_router
from app.routers.knowledge import router as knowledge_router
from app.routers.multimodal import router as multimodal_router
from app.routers.camera import router as camera_router
from app.routers.settings import router as settings_router
from app.mcp.server import create_mcp_server
from app.startup import init_on_startup
from contextlib import asynccontextmanager


async def _register_mcp_services() -> None:
    from app.db.session import AsyncSessionLocal
    from app.dependencies import get_chat_service, get_face_service, get_llm_service, get_memory_service
    from app.mcp.registry import MCPToolServices, register_mcp_services

    async with AsyncSessionLocal() as db:
        llm = await get_llm_service(db)
        memory = await get_memory_service()
        face = await get_face_service()
        chat = await get_chat_service(db)

        register_mcp_services(
            MCPToolServices(
                chat_service=chat,
                llm_service=llm,
                memory_service=memory,
                face_service=face,
            )
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize default data on application startup."""
    await init_on_startup()
    await _register_mcp_services()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(admin_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(faces_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(multimodal_router, prefix="/api")
app.include_router(camera_router, prefix="/api")
app.include_router(settings_router, prefix="/api")

mcp_app = create_mcp_server()
app.mount("/mcp", mcp_app)


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint for load balancers and monitoring."""
    return {"status": "ok", "version": settings.VERSION}
