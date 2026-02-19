from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from pathlib import Path

_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_name: str = "AI Rental Copywriter"
    app_version: str = "1.0.0"
    debug: bool = False

    # API Keys
    openai_api_key: str
    supabase_url: str
    supabase_service_key: str

    # OpenAI Models
    generator_model: str = "gpt-4o-mini"
    judge_model: str = "gpt-4o"
    embedding_model: str = "text-embedding-3-small"
    whisper_model: str = "whisper-1"

    # RAG
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k_chunks: int = 5
    top_k_winners: int = 3
    similarity_threshold: float = 0.7

    # Generation
    max_refine_attempts: int = 3
    judge_pass_score: int = 8
    temperature_generator: float = 0.8
    temperature_judge: float = 0.2

    # Timeouts
    openai_timeout: int = 120
    whisper_timeout: int = 300

    # File Upload
    max_file_size_mb: int = 50
    allowed_audio_formats: list[str] = ["mp3", "wav", "m4a", "ogg"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()
