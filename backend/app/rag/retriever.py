import logging
from app.rag.vector_store import search_similar, get_winners
from app.services.embedding_service import get_embedding

logger = logging.getLogger(__name__)


async def retrieve_context(
    query: str,
    niche_id: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    logger.info(f"Buscando contexto: '{query[:50]}...'")
    query_embedding = await get_embedding(query)
    results = await search_similar(
        query_embedding=query_embedding,
        niche_id=niche_id,
        top_k=top_k,
    )
    return results


async def retrieve_winners(
    niche_id: str | None = None,
    vibe_id: str | None = None,
    top_k: int = 3,
) -> list[dict]:
    logger.info(f"Buscando winners: niche={niche_id}, vibe={vibe_id}")
    return await get_winners(niche_id=niche_id, vibe_id=vibe_id, top_k=top_k)
