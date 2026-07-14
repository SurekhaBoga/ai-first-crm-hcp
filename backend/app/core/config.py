"""
Environment-driven application settings, loaded with python-dotenv.

Deliberately a plain class reading os.getenv rather than pydantic-settings:
the approved tech stack lists python-dotenv explicitly, so this is the one
place in the app that touches the environment. Everything else imports
`settings` from here instead of calling os.getenv directly.
"""

import os

from dotenv import load_dotenv

load_dotenv()


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "AI-First CRM HCP API")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    API_V1_PREFIX: str = "/api/v1"

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/hcp_crm",
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    CORS_ORIGINS: list[str] = _split_csv(
        os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    )

    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # AI layer (LangGraph + Groq) — see app/ai/
    GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    GROQ_TIMEOUT_SECONDS: float = float(os.getenv("GROQ_TIMEOUT_SECONDS", "30"))
    AI_MAX_LLM_RETRIES: int = int(os.getenv("AI_MAX_LLM_RETRIES", "2"))


settings = Settings()
