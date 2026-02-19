import logging
from fastapi import APIRouter
from app.models.responses import HealthResponse
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    openai_ok = False
    supabase_ok = False

    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key, timeout=5)
        await client.models.list()
        openai_ok = True
    except Exception as e:
        logger.warning(f"OpenAI check falhou: {e}")

    try:
        from app.rag.vector_store import get_client, _headers, _rest_url
        client = await get_client()
        resp = await client.get(
            _rest_url("niches") + "?select=id&limit=1",
            headers=_headers(),
        )
        resp.raise_for_status()
        supabase_ok = True
    except Exception as e:
        logger.warning(f"Supabase check falhou: {e}")

    return HealthResponse(
        status="healthy" if openai_ok and supabase_ok else "degraded",
        version=settings.app_version,
        openai_connected=openai_ok,
        supabase_connected=supabase_ok,
    )
