"""Embedding providers.

* ``hash``   - deterministic feature hashing of words/bigrams. No network, no
               keys, no model download. A lexical baseline: good for tests, CI
               and free-tier demos.
* ``openai`` - real semantic embeddings via the OpenAI embeddings API,
               requested at 384 dimensions to match the schema.
"""

import hashlib
import math
import re

import config
import httpx

_STOPWORDS = frozenset(
    "a an the and or but if of to in on at by for with from as is are was were be "
    "been it its this that these those i you we they he she my your our do does did "
    "can could should would will how what when where which who why not no so than "
    "then there about into over".split()
)


def _tokens(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOPWORDS and len(w) > 1]


def _stem(word: str) -> str:
    for suffix in ("ing", "ed", "es", "s"):
        if word.endswith(suffix) and len(word) - len(suffix) >= 3:
            return word[: -len(suffix)]
    return word


def hash_embed(text: str, dim: int = config.EMBEDDING_DIM) -> list[float]:
    words = [_stem(w) for w in _tokens(text)]
    features = words + [f"{a}_{b}" for a, b in zip(words, words[1:])]
    vec = [0.0] * dim
    for feature in features:
        digest = hashlib.blake2b(feature.encode(), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        sign = 1.0 if (value >> 63) & 1 else -1.0
        vec[value % dim] += sign * (1.0 if "_" not in feature else 0.5)
    norm = math.sqrt(sum(v * v for v in vec))
    return [v / norm for v in vec] if norm else vec


def _openai_embed(texts: list[str]) -> list[list[float]]:
    if not config.OPENAI_API_KEY:
        raise RuntimeError("EMBEDDING_PROVIDER=openai requires OPENAI_API_KEY")
    response = httpx.post(
        "https://api.openai.com/v1/embeddings",
        headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
        json={
            "model": config.OPENAI_EMBEDDING_MODEL,
            "input": texts,
            "dimensions": config.EMBEDDING_DIM,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = sorted(response.json()["data"], key=lambda d: d["index"])
    return [d["embedding"] for d in data]


def embed(texts: list[str]) -> list[list[float]]:
    if config.EMBEDDING_PROVIDER == "hash":
        return [hash_embed(t) for t in texts]
    if config.EMBEDDING_PROVIDER == "openai":
        return _openai_embed(texts)
    raise RuntimeError(f"unknown EMBEDDING_PROVIDER: {config.EMBEDDING_PROVIDER}")
