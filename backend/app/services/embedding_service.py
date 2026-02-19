import logging
import hashlib
from openai import AsyncOpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

_client: AsyncOpenAI | None = None
_cache: dict[str, list[float]] = {}


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(api_key=settings.openai_api_key)
    return _client


def _cache_key(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()


async def get_embedding(text: str) -> list[float]:
    key = _cache_key(text)
    if key in _cache:
        logger.debug("Embedding cache hit")
        return _cache[key]

    client = _get_client()
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=text,
    )
    embedding = response.data[0].embedding
    _cache[key] = embedding
    logger.debug(f"Embedding: {len(embedding)} dims")
    return embedding


async def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    logger.info(f"Batch embedding: {len(texts)} textos")
    client = _get_client()
    response = await client.embeddings.create(
        model=settings.embedding_model,
        input=texts,
    )
    embeddings = [item.embedding for item in response.data]
    for text, emb in zip(texts, embeddings):
        _cache[_cache_key(text)] = emb
    return embeddings
