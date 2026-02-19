import logging
from openai import AsyncOpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def process_audio(file_path: str, language: str = "pt") -> str:
    logger.info(f"Transcrevendo áudio: {file_path}, idioma: {language}")
    try:
        client = AsyncOpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.whisper_timeout,
        )
        with open(file_path, "rb") as f:
            transcript = await client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=f,
                language=language,
                response_format="text",
            )
        markdown = f"# Transcrição de Áudio\n\n{transcript}"
        logger.info(f"Transcrito: {len(transcript)} caracteres")
        return markdown
    except Exception as e:
        logger.error(f"Erro na transcrição: {e}", exc_info=True)
        raise ValueError(f"Falha na transcrição: {e}")
