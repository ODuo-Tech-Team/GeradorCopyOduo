import tiktoken
from functools import lru_cache


@lru_cache(maxsize=128)
def count_tokens(text: str, model: str = "gpt-4") -> int:
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def estimate_cost(tokens: int, model: str) -> float:
    pricing = {
        "gpt-4o-mini": 0.0003 / 1000,
        "gpt-4o": 0.005 / 1000,
        "text-embedding-3-small": 0.00002 / 1000,
    }
    rate = pricing.get(model, 0.0003 / 1000)
    return tokens * rate
