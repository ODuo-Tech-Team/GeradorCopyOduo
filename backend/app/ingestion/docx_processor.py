import logging
import re
from docx import Document

logger = logging.getLogger(__name__)


async def process_docx(file_path: str) -> str:
    logger.info(f"Processando DOCX: {file_path}")
    try:
        doc = Document(file_path)
        blocks = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue
            if para.style and para.style.name.startswith("Heading"):
                blocks.append(f"## {text}")
            else:
                blocks.append(text)

        markdown = "\n\n".join(blocks)
        markdown = _clean(markdown)
        logger.info(f"Extraídos {len(markdown)} caracteres do DOCX")
        return markdown
    except Exception as e:
        logger.error(f"Erro no DOCX: {e}", exc_info=True)
        raise ValueError(f"Falha ao processar DOCX: {e}")


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
