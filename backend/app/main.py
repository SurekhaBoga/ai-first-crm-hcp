from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.logging import configure_logging
from app.middleware.request_logging import RequestLoggingMiddleware
from app.routers import ai, chat_history, doctors, health, interactions, users

configure_logging()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.2.0",
    description="Backend for the AI-First CRM HCP Interaction Module — Users, Doctors, "
    "Interactions, Chat History, and a LangGraph-orchestrated AI layer (no auth yet).",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)

register_exception_handlers(app)

app.include_router(health.router)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(doctors.router, prefix=settings.API_V1_PREFIX)
app.include_router(interactions.router, prefix=settings.API_V1_PREFIX)
app.include_router(chat_history.router, prefix=settings.API_V1_PREFIX)
app.include_router(ai.router, prefix=settings.API_V1_PREFIX)


@app.get("/", tags=["root"])
def read_root():
    return {"name": settings.APP_NAME, "version": app.version, "docs": "/docs"}
