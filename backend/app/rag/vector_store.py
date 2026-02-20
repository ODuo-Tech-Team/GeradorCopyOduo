import logging
import json
from uuid import uuid4
import httpx
from app.config import get_settings
from app.models.domain import GenerationResult, VibeEnum

logger = logging.getLogger(__name__)
settings = get_settings()

_client: httpx.AsyncClient | None = None


def _headers() -> dict:
    return {
        "apikey": settings.supabase_service_key,
        "Authorization": f"Bearer {settings.supabase_service_key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def _rest_url(table: str) -> str:
    return f"{settings.supabase_url}/rest/v1/{table}"


def _rpc_url(fn: str) -> str:
    return f"{settings.supabase_url}/rest/v1/rpc/{fn}"


async def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client


async def insert_chunks(
    chunks: list[str],
    embeddings: list[list[float]],
    asset_id: str,
    niche_id: str | None,
    source_type: str = "pdf",
) -> int:
    client = await get_client()
    records = []
    for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        records.append({
            "id": str(uuid4()),
            "embedding": embedding,
            "asset_id": asset_id,
            "chunk_text": chunk,
            "chunk_hash": str(hash(chunk)),
            "chunk_index": idx,
            "chunk_size": len(chunk),
            "niche_id": niche_id,
            "source_type": source_type,
        })
    resp = await client.post(_rest_url("embeddings"), headers=_headers(), json=records)
    resp.raise_for_status()
    logger.info(f"Inseridos {len(records)} chunks")
    return len(records)


async def search_similar(
    query_embedding: list[float],
    niche_id: str | None = None,
    top_k: int = 5,
) -> list[dict]:
    client = await get_client()
    # pgvector RPC expects vector as string "[0.1, 0.2, ...]" not JSON array
    embedding_str = "[" + ",".join(str(v) for v in query_embedding) + "]"
    params = {
        "query_embedding": embedding_str,
        "match_threshold": 0.3,
        "match_count": top_k,
    }
    if niche_id:
        params["filter_niche_id"] = niche_id

    resp = await client.post(_rpc_url("search_similar_embeddings"), headers=_headers(), json=params)
    resp.raise_for_status()
    data = resp.json()
    logger.info(f"Busca vetorial: {len(data)} resultados (threshold=0.3)")
    return data


async def get_winners(
    niche_id: str | None = None,
    vibe_id: str | None = None,
    top_k: int = 3,
) -> list[dict]:
    client = await get_client()
    if niche_id and vibe_id:
        resp = await client.post(_rpc_url("get_fewshot_examples"), headers=_headers(), json={
            "p_niche_id": niche_id,
            "p_vibe_id": vibe_id,
            "max_examples": top_k,
        })
        resp.raise_for_status()
        return resp.json()

    url = _rest_url("winners") + f"?select=*&order=marked_winner_at.desc&limit={top_k}"
    if niche_id:
        url += f"&niche_id=eq.{niche_id}"
    resp = await client.get(url, headers=_headers())
    resp.raise_for_status()
    return resp.json()


async def save_generation_result(
    generation_id: str,
    niche: str,
    niche_id: str | None,
    vibe_id: str | None,
    briefing: str,
    vibe: VibeEnum,
    result: GenerationResult,
    judge_score: int | None,
    refine_count: int,
    tokens_used: int,
) -> None:
    client = await get_client()
    record = {
        "id": generation_id,
        "briefing_text": briefing,
        "niche_id": niche_id,
        "vibe_id": vibe_id,
        "options": result.model_dump()["options"],
        "judge_feedback": {"score": judge_score} if judge_score else None,
        "status": "completed",
        "retry_count": refine_count,
        "tokens_used": tokens_used,
    }
    record = {k: v for k, v in record.items() if v is not None}
    resp = await client.post(_rest_url("generations"), headers=_headers(), json=record)
    resp.raise_for_status()
    logger.info(f"Geração salva: {generation_id}")


async def list_generations(limit: int = 50, offset: int = 0) -> list[dict]:
    """Lista gerações ordenadas por data, mais recentes primeiro."""
    client = await get_client()
    url = (
        _rest_url("generations")
        + f"?select=id,briefing_text,niche_id,vibe_id,status,judge_feedback,created_at"
        + f"&order=created_at.desc"
        + f"&limit={limit}&offset={offset}"
    )
    resp = await client.get(url, headers=_headers())
    resp.raise_for_status()
    return resp.json()


async def get_generation_by_id(generation_id: str) -> dict | None:
    """Busca uma geração completa por ID, incluindo options."""
    client = await get_client()
    url = (
        _rest_url("generations")
        + f"?select=id,briefing_text,niche_id,vibe_id,status,options,judge_feedback,retry_count,tokens_used,created_at"
        + f"&id=eq.{generation_id}"
        + "&limit=1"
    )
    resp = await client.get(url, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    return data[0] if data else None


async def get_generation_stats() -> dict:
    """Retorna contagens para o dashboard."""
    client = await get_client()
    count_headers = {**_headers(), "Prefer": "count=exact", "Range-Unit": "items", "Range": "0-0"}

    gen_resp = await client.get(_rest_url("generations") + "?select=id", headers=count_headers)
    gen_count = int(gen_resp.headers.get("content-range", "*/0").split("/")[-1] or 0)

    assets_resp = await client.get(_rest_url("assets") + "?select=id", headers=count_headers)
    assets_count = int(assets_resp.headers.get("content-range", "*/0").split("/")[-1] or 0)

    winners_resp = await client.get(_rest_url("winners") + "?select=id", headers=count_headers)
    winners_count = int(winners_resp.headers.get("content-range", "*/0").split("/")[-1] or 0)

    return {
        "total_generations": gen_count,
        "total_assets": assets_count,
        "total_winners": winners_count,
    }
