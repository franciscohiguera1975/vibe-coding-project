from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import get_settings
from app.interfaces.http.exception_handlers import register_exception_handlers
from app.interfaces.http.routers.agent import router as agent_router
from app.interfaces.http.routers.ai import router as ai_router
from app.interfaces.http.routers.audit import router as audit_router
from app.interfaces.http.routers.auth import router as auth_router
from app.interfaces.http.routers.catalog import router as catalog_router
from app.interfaces.http.routers.configurations import router as configurations_router
from app.interfaces.http.routers.health import router as health_router
from app.interfaces.http.routers.images import router as images_router
from app.interfaces.http.routers.practices import router as practices_router
from app.interfaces.http.routers.rag import router as rag_router
from app.interfaces.http.routers.roles import permissions_router
from app.interfaces.http.routers.roles import router as roles_router
from app.interfaces.http.routers.storage import router as storage_router
from app.interfaces.http.routers.users import router as users_router

settings = get_settings()

app = FastAPI(
    title="Vibe Coding Platform API",
    description="Plataforma de enseñanza práctica de Vibe Coding con FastAPI, IA e IA Agéntica.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(health_router)
app.include_router(auth_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(roles_router, prefix="/api")
app.include_router(permissions_router, prefix="/api")
app.include_router(practices_router, prefix="/api")
app.include_router(catalog_router, prefix="/api")
app.include_router(configurations_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(agent_router, prefix="/api")
app.include_router(images_router, prefix="/api")
app.include_router(storage_router, prefix="/api")
app.include_router(rag_router, prefix="/api")
