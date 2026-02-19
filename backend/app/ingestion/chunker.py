import logging
import tiktoken

logger = logging.getLogger(__name__)


def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 50,
    encoding_name: str = "cl100k_base",
) -> list[str]:
    logger.info(f"Chunking: {len(text)} chars, {chunk_size} tokens/chunk")
    try:
        encoding = tiktoken.get_encoding(encoding_name)
        tokens = encoding.encode(text)
        chunks = []
        start = 0
        while start < len(tokens):
            end = start + chunk_size
            chunk_tokens = tokens[start:end]
            chunks.append(encoding.decode(chunk_tokens))
            start += chunk_size - chunk_overlap
        logger.info(f"Criados {len(chunks)} chunks de {len(tokens)} tokens")
        return chunks
    except Exception as e:
        logger.error(f"Chunking falhou: {e}")
        # Fallback simples
        char_size = chunk_size * 4
        return [text[i : i + char_size] for i in range(0, len(text), char_size)]
