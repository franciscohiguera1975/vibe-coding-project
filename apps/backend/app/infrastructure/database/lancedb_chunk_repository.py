"""Implementacion de NormativaChunkRepository sobre LanceDB (base de datos
vectorial embebida — corre en el mismo proceso que la consulta, como SQLite,
por eso vive en el VPS junto al backend y no en el HPC; ver
docs/saturdays_ai/00-plan.md §5 y §9 para el razonamiento completo).

`search_hybrid` resuelve la recuperacion hibrida (vector + BM25, fusionados
con RRF) dentro de LanceDB: coseno EXACTO sobre `embedding` (sin indice ANN,
ver nota en `_ensure_indexes` sobre por que un IVF-PQ degrada el recall a
este tamano de corpus), indice FTS (Tantivy, BM25 real, stemming en espanol)
sobre `text`, y `RRFReranker(K=60)` para fusionar — mismo k=60 que usan
Elasticsearch/OpenSearch por defecto. Reemplaza una version anterior que
hacia esta fusion a mano en Python sobre `list_all()` (fuerza bruta): medido
contra el corpus real (896 chunks), list_all() + Python ≈800ms vs.
search_hybrid() ≈100-200ms — mas lento que un ANN, pero exacto, y todavia
varias veces mas rapido que materializar las 896 filas a objetos Python en
cada consulta.

La tabla se crea de forma perezosa (lazy) en el primer upsert, infiriendo la
dimension del vector embedding del primer chunk insertado: 128 en modo mock
(ver MockRagAdapter), 1024 para el modelo real `intfloat/multilingual-e5-large`
servido por TEI. Nunca se hardcodea un tamano fijo porque mock y produccion
difieren.

`upsert` hace delete-then-insert (LanceDB no impone unicidad nativa sobre
columnas arbitrarias) para preservar exactamente la misma garantia de
idempotencia que tenia la version SQLAlchemy — `chunk_id` sigue siendo la
clave natural estable que usa scripts/rag/load_chunks.py."""

from __future__ import annotations

from pathlib import Path

import lancedb
import pyarrow as pa
from lancedb.index import FTS
from lancedb.rerankers import RRFReranker

from app.domain.entities.rag import NormativaChunk, RetrievedChunk

# Mismo valor (60) que usan Elasticsearch/OpenSearch por defecto para su
# propia fusion RRF — ver docs/saturdays_ai/00-plan.md §9.
_RRF_K = 60


def _schema_for_dimension(dimension: int) -> pa.Schema:
    return pa.schema(
        [
            pa.field("chunk_id", pa.string()),
            pa.field("source_document", pa.string()),
            pa.field("article_label", pa.string()),
            pa.field("text", pa.string()),
            pa.field("embedding", pa.list_(pa.float32(), dimension)),
        ]
    )


def _row_to_chunk(row: dict) -> NormativaChunk:
    # Sin id/created_at/updated_at: LanceDB no necesita una clave surrogate, y
    # nada rio abajo (los casos de uso) lee esos campos de un NormativaChunk
    # (ver docs/saturdays_ai/00-plan.md).
    embedding = row.get("embedding")
    return NormativaChunk(
        chunk_id=row["chunk_id"],
        source_document=row["source_document"],
        article_label=row["article_label"],
        text=row["text"],
        embedding=list(embedding) if embedding is not None else [],
    )


def _chunk_to_row(chunk: NormativaChunk) -> dict:
    return {
        "chunk_id": chunk.chunk_id,
        "source_document": chunk.source_document,
        "article_label": chunk.article_label,
        "text": chunk.text,
        "embedding": list(chunk.embedding) if chunk.embedding else [],
    }


def _escape(value: str) -> str:
    # Filtros de LanceDB son SQL — escapar comillas simples basta porque
    # chunk_id siempre viene de chunks.jsonl (dato propio, no input de usuario).
    return value.replace("'", "''")


class LanceDbNormativaChunkRepository:
    """Un `NormativaChunkRepository` (Protocol de app.domain.repositories.rag_repository)
    respaldado por una tabla LanceDB en `db_path` (se crea el directorio si no
    existe)."""

    def __init__(self, db_path: str, table_name: str = "normativa_chunks") -> None:
        self._table_name = table_name
        Path(db_path).mkdir(parents=True, exist_ok=True)
        self._db = lancedb.connect(db_path)

    def _open_table(self):
        try:
            return self._db.open_table(self._table_name)
        except (ValueError, FileNotFoundError):
            return None

    def _open_or_create_table(self, dimension: int):
        table = self._open_table()
        if table is not None:
            return table
        return self._db.create_table(self._table_name, schema=_schema_for_dimension(dimension))

    def get_by_chunk_id(self, chunk_id: str) -> NormativaChunk | None:
        table = self._open_table()
        if table is None:
            return None
        rows = table.search().where(f"chunk_id = '{_escape(chunk_id)}'").limit(1).to_list()
        return _row_to_chunk(rows[0]) if rows else None

    def upsert(self, chunk: NormativaChunk) -> NormativaChunk:
        if not chunk.embedding:
            raise ValueError(
                "NormativaChunk.embedding no puede estar vacio para upsert en LanceDB "
                "(la dimension del vector se infiere del primer chunk insertado)"
            )
        table = self._open_or_create_table(len(chunk.embedding))
        table.delete(f"chunk_id = '{_escape(chunk.chunk_id)}'")
        table.add([_chunk_to_row(chunk)])
        return chunk

    def list_all(self) -> list[NormativaChunk]:
        table = self._open_table()
        if table is None:
            return []
        return [_row_to_chunk(row) for row in table.search().to_list()]

    def count(self) -> int:
        table = self._open_table()
        return table.count_rows() if table is not None else 0

    def search_hybrid(
        self, query_embedding: list[float], query_text: str, *, k: int = 3
    ) -> list[RetrievedChunk]:
        table = self._open_table()
        if table is None or table.count_rows() == 0:
            return []
        self._ensure_indexes(table)
        rows = (
            table.search(query_type="hybrid")
            .vector(query_embedding)
            .text(query_text or " ")
            .metric("cosine")
            .bypass_vector_index()
            .rerank(reranker=RRFReranker(K=_RRF_K))
            .limit(k)
            .to_list()
        )
        return [
            RetrievedChunk(chunk=_row_to_chunk(row), score=row.get("_relevance_score", 0.0))
            for row in rows
        ]

    def _ensure_indexes(self, table) -> None:
        """Crea el indice de texto (FTS/BM25, con stemming en espanol — el
        corpus de normativa es 100% espanol) si no existe todavia —
        idempotente y barato de chequear (`list_indices()` es ~1-2ms), a
        diferencia de crearlo (~100-200ms), por eso se evita recrearlo en
        cada busqueda.

        Deliberadamente NO se crea un indice vectorial (IVF-PQ): es una
        aproximacion (ANN), y a este tamano de corpus (~900 filas) degrada el
        recall de forma medible sin ganancia real de velocidad (ver
        bypass_vector_index() en search_hybrid, que fuerza coseno exacto). IVF-PQ
        esta pensado para corpus de miles/millones de filas, donde la busqueda
        exacta si se vuelve el cuello de botella — no es el caso aqui."""
        existing = {idx.columns[0] for idx in table.list_indices()}
        if "text" not in existing:
            table.create_index("text", config=FTS(language="Spanish"))
