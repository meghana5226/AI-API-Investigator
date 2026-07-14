"""
Application configuration loaded from environment variables.
Uses pydantic-settings so every value is validated at startup instead
of failing silently deep inside the request lifecycle.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # App
    PROJECT_NAME: str = "AI API Investigator"
    API_V1_PREFIX: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = "change-this-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/ai_api_investigator"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # Vector store / AI
    CHROMA_PERSIST_DIR: str = "chroma_data"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # Which LLM backend to use: "ollama" (self-hosted, free, needs a beefy
    # machine for good speed) or "groq" (hosted, free tier, fast, needs
    # GROQ_API_KEY from https://console.groq.com). Everything else in the AI
    # pipeline (RAG, caching, risk detection) is identical either way --
    # only llm_service.py branches on this setting.
    LLM_PROVIDER: str = "ollama"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    # qwen2.5:7b gives the best answers but can take 1-3+ minutes per response
    # on a CPU-only machine (no GPU). If AI responses are timing out or you'd
    # rather have fast iteration while testing, switch to a smaller model --
    # pull it first with: docker compose exec ollama ollama pull qwen2.5:1.5b
    OLLAMA_MODEL: str = "qwen2.5:7b"

    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # CPU-only inference of a 7B model can genuinely take 1-3+ minutes,
    # especially on the first request after the model isn't already loaded
    # in memory. 60s was too aggressive and caused false "AI unavailable"
    # fallbacks on machines without a GPU -- 4 minutes gives real headroom
    # while still failing fast enough to not hang a request forever. (Groq
    # responses return in a couple seconds in practice, so this ceiling is
    # rarely hit when LLM_PROVIDER=groq.)
    AI_REQUEST_TIMEOUT_SECONDS: int = 240

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # AI result caching (Redis) -- avoids re-calling the LLM for identical
    # summary/explanation requests within this window.
    AI_CACHE_TTL_SECONDS: int = 60 * 60 * 24  # 24 hours

    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
