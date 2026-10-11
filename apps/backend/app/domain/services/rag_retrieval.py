"""Recuperacion hibrida: BM25 (palabra clave) + similitud de coseno (semantica),
fusionadas por Reciprocal Rank Fusion (RRF) — mismo patron que un motor de
busqueda hibrido estandar (keyword + vector), sin necesidad de un motor de
busqueda aparte: BM25Okapi (rank-bm25) corre en memoria sobre el texto de los
chunks ya cargados, y el coseno corre sobre los embeddings ya calculados (ver
docs/saturdays_ai/00-plan.md §5: unos cientos de filas hacen que todo esto sea
trivial en memoria para el VPS pequeno que sirve la plataforma). Sin IO propio:
recibe los chunks ya cargados, el embedding de la consulta y su texto crudo."""

from __future__ import annotations

import math
import re

from rank_bm25 import BM25Okapi

from app.domain.entities.rag import NormativaChunk, RetrievedChunk

# Constante estandar de RRF (score = 1 / (RRF_K + rank), rank 1-indexado) — el
# mismo valor (60) que usan Elasticsearch/OpenSearch por defecto para su propia
# implementacion de RRF; no es un hiperparametro que este proyecto haya tenido
# que ajustar.
_RRF_K = 60

_TOKEN_RE = re.compile(r"[a-záéíóúñü0-9]+")


def cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b, strict=False))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


def _vector_ranking(query_embedding: list[float], chunks: list[NormativaChunk]) -> list[str]:
    """IDs de `chunks` ordenados por similitud de coseno descendente."""
    scored = [(c.chunk_id, cosine_similarity(query_embedding, c.embedding)) for c in chunks]
    scored.sort(key=lambda pair: pair[1], reverse=True)
    return [chunk_id for chunk_id, _ in scored]


def _bm25_ranking(query_text: str, chunks: list[NormativaChunk]) -> list[str]:
    """IDs de `chunks` ordenados por score BM25 descendente sobre su texto."""
    if not query_text.strip():
        return []
    return Bm25Index(chunks).rank(query_text)


class Bm25Index:
    """Indice BM25 precomputado sobre un conjunto fijo de chunks, para
    reusarlo entre varias consultas dentro de una misma ejecucion (p.ej. las 5
    preguntas de ValidateSyllabusUseCase o las 15 de RunRagEvaluationUseCase)
    sin repetir la tokenizacion y el precomputo de BM25Okapi en cada una —
    sobre ~900 chunks eso es barato una vez, pero no gratis 5-15 veces
    seguidas en el VPS pequeno que sirve el resto de la plataforma."""

    def __init__(self, chunks: list[NormativaChunk]) -> None:
        self._chunk_ids = [c.chunk_id for c in chunks]
        # BM25Okapi divide por el tamano del corpus en su constructor — con
        # cero chunks (normativa aun no cargada, ver load_chunks.py) lanzaria
        # ZeroDivisionError antes de que nada llegue a usarlo.
        self._model = BM25Okapi([_tokenize(c.text) for c in chunks]) if chunks else None

    def rank(self, query_text: str) -> list[str]:
        if not query_text.strip() or self._model is None:
            return []
        scores = self._model.get_scores(_tokenize(query_text))
        pairs = zip(self._chunk_ids, scores, strict=True)
        ranked = sorted(pairs, key=lambda pair: pair[1], reverse=True)
        return [chunk_id for chunk_id, _ in ranked]


def build_bm25_index(chunks: list[NormativaChunk]) -> Bm25Index:
    """Construye el indice BM25 una sola vez sobre el mismo subconjunto
    candidato que usa `retrieve_top_k` (chunks con embedding ya cargado), para
    pasarselo a varias llamadas de `retrieve_top_k` dentro de una misma
    ejecucion via el parametro `bm25_index`."""
    return Bm25Index([c for c in chunks if c.embedding])


def _reciprocal_rank_fusion(rankings: list[list[str]], *, k: int = _RRF_K) -> dict[str, float]:
    """RRF: score(doc) = sum(1 / (k + rank)) sobre cada ranking donde aparece
    (rank 1-indexado). Ignora el score crudo de cada metodo — solo usa la
    posicion — asi BM25 (puntajes sin acotar) y coseno (acotado a [-1, 1]) se
    combinan sin que uno domine al otro por escala."""
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank, chunk_id in enumerate(ranking, start=1):
            fused[chunk_id] = fused.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return fused


def retrieve_top_k(
    query_embedding: list[float],
    query_text: str,
    chunks: list[NormativaChunk],
    *,
    k: int = 3,
    bm25_index: Bm25Index | None = None,
) -> list[RetrievedChunk]:
    """Recuperacion hibrida: fusiona el ranking vectorial (coseno sobre
    `query_embedding`) y el ranking por palabra clave (BM25 sobre
    `query_text`) con Reciprocal Rank Fusion, y devuelve los `k` chunks con
    mayor score fusionado. `RetrievedChunk.score` pasa a ser ese score RRF, no
    el coseno crudo. Ignora chunks sin embedding (aun no cargados, ver
    scripts/rag/load_chunks.py) — BM25 solo se calcula sobre ese mismo
    subconjunto, para no recomendar un chunk por coincidencia de palabras si
    todavia no tiene embedding (i.e., no esta realmente listo).

    `bm25_index` es OPCIONAL: si el llamador va a llamar esta funcion varias
    veces seguidas sobre el mismo `chunks` (p.ej. una vez por item del
    checklist, o una vez por pregunta de evaluacion), debe construirlo una
    sola vez con `build_bm25_index(chunks)` y pasarlo aqui, para no repetir la
    indexacion BM25 en cada sub-consulta. Sin el, se reconstruye al vuelo
    (comportamiento identico, solo mas repetitivo)."""
    candidates = [c for c in chunks if c.embedding]
    if not candidates:
        return []

    vector_ranking = _vector_ranking(query_embedding, candidates)
    bm25_ranking = bm25_index.rank(query_text) if bm25_index is not None else _bm25_ranking(
        query_text, candidates
    )
    fused_scores = _reciprocal_rank_fusion([vector_ranking, bm25_ranking])

    by_id = {c.chunk_id: c for c in candidates}
    ordered_ids = sorted(fused_scores, key=lambda cid: fused_scores[cid], reverse=True)
    return [
        RetrievedChunk(chunk=by_id[chunk_id], score=fused_scores[chunk_id])
        for chunk_id in ordered_ids[:k]
    ]
