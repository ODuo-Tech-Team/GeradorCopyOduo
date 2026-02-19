import logging
import tempfile
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.models.responses import IngestResponse
from app.services.ingestion_service import IngestionService
from app.rag.vector_store import get_client, _headers, _rest_url
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()


@router.get("/assets")
async def list_assets():
    """Lista todos os assets com contagem de chunks."""
    client = await get_client()
    url = _rest_url("assets") + "?select=id,file_name,processing_status,created_at&order=created_at.desc&limit=50"
    resp = await client.get(url, headers=_headers())
    resp.raise_for_status()
    assets = resp.json()

    # Buscar contagem de chunks por asset
    for asset in assets:
        chunks_url = _rest_url("embeddings") + f"?asset_id=eq.{asset['id']}&select=id"
        chunks_resp = await client.get(chunks_url, headers={**_headers(), "Prefer": "count=exact"})
        count = chunks_resp.headers.get("content-range", "*/0").split("/")[-1]
        asset["chunks_count"] = int(count) if count != "*" else 0

    return assets


@router.post("/pdf", response_model=IngestResponse)
async def ingest_pdf(
    file: UploadFile = File(...),
    niche: str = Form(...),
    niche_id: str = Form(None),
    is_winner: bool = Form(False),
):
    logger.info(f"Upload PDF: {file.filename}, nicho={niche}")

    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(400, "Apenas arquivos PDF são aceitos")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(413, f"Arquivo muito grande: {size_mb:.1f}MB (máx: {settings.max_file_size_mb}MB)")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        service = IngestionService()
        chunks, asset_id = await service.ingest_pdf(tmp_path, niche_id, is_winner)
        return IngestResponse(
            success=True,
            chunks_created=chunks,
            file_name=file.filename,
            niche=niche,
            message=f"PDF processado: {chunks} chunks criados",
        )
    except Exception as e:
        logger.error(f"Erro na ingestão: {e}", exc_info=True)
        raise HTTPException(500, f"Falha na ingestão: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/docx", response_model=IngestResponse)
async def ingest_docx(
    file: UploadFile = File(...),
    niche: str = Form(...),
    niche_id: str = Form(None),
):
    logger.info(f"Upload DOCX: {file.filename}, nicho={niche}")

    if not file.filename or not file.filename.endswith((".docx", ".doc")):
        raise HTTPException(400, "Apenas arquivos DOCX são aceitos")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(413, f"Arquivo muito grande: {size_mb:.1f}MB (máx: {settings.max_file_size_mb}MB)")

    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        service = IngestionService()
        chunks, asset_id = await service.ingest_docx(tmp_path, niche_id)
        return IngestResponse(
            success=True,
            chunks_created=chunks,
            file_name=file.filename,
            niche=niche,
            message=f"DOCX processado: {chunks} chunks criados",
        )
    except Exception as e:
        logger.error(f"Erro na ingestão DOCX: {e}", exc_info=True)
        raise HTTPException(500, f"Falha na ingestão: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@router.post("/audio", response_model=IngestResponse)
async def ingest_audio(
    file: UploadFile = File(...),
    niche: str = Form(...),
    niche_id: str = Form(None),
    language: str = Form("pt"),
):
    logger.info(f"Upload áudio: {file.filename}, nicho={niche}")

    ext = Path(file.filename).suffix[1:].lower() if file.filename else ""
    if ext not in settings.allowed_audio_formats:
        raise HTTPException(400, f"Formato inválido. Aceitos: {settings.allowed_audio_formats}")

    content = await file.read()
    size_mb = len(content) / (1024 * 1024)
    if size_mb > settings.max_file_size_mb:
        raise HTTPException(413, f"Arquivo muito grande: {size_mb:.1f}MB")

    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        service = IngestionService()
        chunks, asset_id = await service.ingest_audio(tmp_path, niche_id, language)
        return IngestResponse(
            success=True,
            chunks_created=chunks,
            file_name=file.filename or "audio",
            niche=niche,
            message=f"Áudio transcrito e processado: {chunks} chunks criados",
        )
    except Exception as e:
        logger.error(f"Erro na ingestão: {e}", exc_info=True)
        raise HTTPException(500, f"Falha na ingestão: {e}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)
