"""Recuperacion por similitud de coseno, fuerza bruta en Python (ver
docs/saturdays_ai/00-plan.md §5: decision explicita de NO usar una base de datos
vectorial — unos cientos de filas hacen que una comparacion en memoria sea
trivial para el VPS pequeno que sirve la plataforma). Sin IO ni dependencias de
framework: recibe los chunks ya cargados y el embedding de la consulta."""

from __future__ import annotations

import math

from app.domain.entities.rag import NormativaChunk, RetrievedChunk


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def retrieve_top_k(
    query_embedding: list[float],
    chunks: list[NormativaChunk],
    *,
    k: int = 3,
) -> list[RetrievedChunk]:
    """Devuelve los `k` chunks mas similares a `query_embedding`, ordenados de
    mayor a menor score. Ignora chunks sin embedding (aun no cargados, ver
    scripts/rag/load_chunks.py)."""
    scored = [
        RetrievedChunk(chunk=chunk, score=cosine_similarity(query_embedding, chunk.embedding))
        for chunk in chunks
        if chunk.embedding
    ]
    scored.sort(key=lambda r: r.score, reverse=True)
    return scored[:k]
