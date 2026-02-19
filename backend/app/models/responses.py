from pydantic import BaseModel, Field
from app.models.domain import CarouselOption


class GenerateResponse(BaseModel):
    success: bool
    generation_id: str
    options: list[CarouselOption]
    metadata: dict = Field(default_factory=dict)


class IngestResponse(BaseModel):
    success: bool
    chunks_created: int
    file_name: str
    niche: str
    message: str


class HealthResponse(BaseModel):
    status: str
    version: str
    openai_connected: bool
    supabase_connected: bool
