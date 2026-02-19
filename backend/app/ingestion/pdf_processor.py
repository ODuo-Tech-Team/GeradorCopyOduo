import logging
import re
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


async def process_pdf(file_path: str) -> str:
    logger.info(f"Processando PDF: {file_path}")
    try:
        doc = fitz.open(file_path)
        blocks = []
        for page_num, page in enumerate(doc, 1):
            text = page.get_text("text")
            if text.strip():
                blocks.append(f"## Página {page_num}\n\n{text.strip()}")
        doc.close()

        markdown = "\n\n".join(blocks)
        markdown = _clean(markdown)
        logger.info(f"Extraídos {len(markdown)} caracteres de {len(blocks)} páginas")
        return markdown
    except Exception as e:
        logger.error(f"Erro no PDF: {e}", exc_info=True)
        raise ValueError(f"Falha ao processar PDF: {e}")


def _clean(text: str) -> str:
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"\n\d+\n", "\n", text)
    text = re.sub(r"Page \d+ of \d+", "", text)
    return text.strip()
