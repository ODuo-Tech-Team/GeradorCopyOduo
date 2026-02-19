from pydantic import BaseModel, Field
from app.models.domain import VibeEnum


class GenerateRequest(BaseModel):
    niche: str = Field(min_length=1, description="Nicho de locação")
    briefing: str = Field(min_length=10, max_length=2000, description="Briefing do conteúdo")
    vibe: VibeEnum = Field(description="Tom da copy")
    niche_id: str | None = Field(None, description="UUID do nicho no Supabase")
    vibe_id: str | None = Field(None, description="UUID do vibe no Supabase")


class IngestPDFRequest(BaseModel):
    niche: str
    niche_id: str | None = None
    is_winner: bool = False


class IngestAudioRequest(BaseModel):
    niche: str
    niche_id: str | None = None
    language: str = "pt"
