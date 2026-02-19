import logging
from pathlib import Path
from uuid import uuid4
from app.ingestion.pdf_processor import process_pdf
from app.ingestion.docx_processor import process_docx
from app.ingestion.audio_processor import process_audio
from app.ingestion.chunker import chunk_text
from app.services.embedding_service import get_embeddings_batch
from app.rag.vector_store import insert_chunks, get_client, _headers, _rest_url
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class IngestionService:
    async def _insert_asset(self, data: dict) -> None:
        client = await get_client()
        resp = await client.post(_rest_url("assets"), headers=_headers(), json=data)
        resp.raise_for_status()

    async def _update_asset(self, asset_id: str, data: dict) -> None:
        client = await get_client()
        url = _rest_url("assets") + f"?id=eq.{asset_id}"
        headers = {**_headers(), "Prefer": "return=minimal"}
        resp = await client.patch(url, headers=headers, json=data)
        resp.raise_for_status()

    async def ingest_pdf(
        self,
        file_path: str,
        niche_id: str | None = None,
        is_winner: bool = False,
    ) -> tuple[int, str]:
        """Retorna (chunks_criados, asset_id)."""
        logger.info(f"Ingerindo PDF: {file_path}")

        asset_id = str(uuid4())
        await self._insert_asset({
            "id": asset_id,
            "file_name": Path(file_path).name,
            "file_type": "pdf",
            "file_size_bytes": Path(file_path).stat().st_size,
            "storage_path": f"assets/{asset_id}/{Path(file_path).name}",
            "mime_type": "application/pdf",
            "processing_status": "processing",
            "niche_id": niche_id,
        })

        try:
            markdown = await process_pdf(file_path)
            chunks = chunk_text(markdown, settings.chunk_size, settings.chunk_overlap)
            embeddings = await get_embeddings_batch(chunks)
            count = await insert_chunks(chunks, embeddings, asset_id, niche_id, "pdf")

            await self._update_asset(asset_id, {
                "processing_status": "completed",
                "markdown_content": markdown,
                "word_count": len(markdown.split()),
            })

            return count, asset_id
        except Exception as e:
            await self._update_asset(asset_id, {
                "processing_status": "failed",
                "processing_error": str(e),
            })
            raise

    async def ingest_docx(
        self,
        file_path: str,
        niche_id: str | None = None,
    ) -> tuple[int, str]:
        """Retorna (chunks_criados, asset_id)."""
        logger.info(f"Ingerindo DOCX: {file_path}")

        asset_id = str(uuid4())
        await self._insert_asset({
            "id": asset_id,
            "file_name": Path(file_path).name,
            "file_type": "pdf",
            "file_size_bytes": Path(file_path).stat().st_size,
            "storage_path": f"assets/{asset_id}/{Path(file_path).name}",
            "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "processing_status": "processing",
            "niche_id": niche_id,
        })

        try:
            markdown = await process_docx(file_path)
            chunks = chunk_text(markdown, settings.chunk_size, settings.chunk_overlap)
            embeddings = await get_embeddings_batch(chunks)
            count = await insert_chunks(chunks, embeddings, asset_id, niche_id, "pdf")

            await self._update_asset(asset_id, {
                "processing_status": "completed",
                "markdown_content": markdown,
                "word_count": len(markdown.split()),
            })

            return count, asset_id
        except Exception as e:
            await self._update_asset(asset_id, {
                "processing_status": "failed",
                "processing_error": str(e),
            })
            raise

    async def ingest_audio(
        self,
        file_path: str,
        niche_id: str | None = None,
        language: str = "pt",
    ) -> tuple[int, str]:
        logger.info(f"Ingerindo áudio: {file_path}")

        asset_id = str(uuid4())
        await self._insert_asset({
            "id": asset_id,
            "file_name": Path(file_path).name,
            "file_type": "audio",
            "file_size_bytes": Path(file_path).stat().st_size,
            "storage_path": f"assets/{asset_id}/{Path(file_path).name}",
            "mime_type": "audio/mpeg",
            "processing_status": "processing",
            "niche_id": niche_id,
        })

        try:
            markdown = await process_audio(file_path, language)
            chunks = chunk_text(markdown, settings.chunk_size, settings.chunk_overlap)
            embeddings = await get_embeddings_batch(chunks)
            count = await insert_chunks(chunks, embeddings, asset_id, niche_id, "audio")

            await self._update_asset(asset_id, {
                "processing_status": "completed",
                "markdown_content": markdown,
                "word_count": len(markdown.split()),
            })

            return count, asset_id
        except Exception as e:
            await self._update_asset(asset_id, {
                "processing_status": "failed",
                "processing_error": str(e),
            })
            raise
