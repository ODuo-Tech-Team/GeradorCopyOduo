from fastapi import APIRouter
from app.api.v1 import health, ingestion, generation

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(ingestion.router, prefix="/ingest", tags=["Ingestão"])
api_router.include_router(generation.router, prefix="/generate", tags=["Geração"])
