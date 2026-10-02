from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.config import get_settings
from app.interfaces.http.exception_handlers import register_exception_handlers
from app.interfaces.http.routers.health import router as health_router

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
