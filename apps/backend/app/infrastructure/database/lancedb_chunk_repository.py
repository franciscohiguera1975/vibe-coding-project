"""Implementacion de NormativaChunkRepository sobre LanceDB (base de datos
vectorial embebida — corre en el mismo proceso que la consulta, como SQLite,
por eso vive en el VPS junto al backend y no en el HPC; ver
docs/saturdays_ai/00-plan.md §5 para el razonamiento completo de esta decision
pedagogica deliberada).

Importante: este adaptador SOLO cambia DONDE viven los chunks+embeddings. La
recuperacion semantica sigue siendo la misma fuerza bruta en Python sobre
`list_all()` (ver app.domain.services.rag_retrieval) — no se usa la busqueda
vectorial nativa de LanceDB, a proposito, para que el cambio quede contenido a
la capa de infraestructura sin tocar el dominio/casos de uso (Protocol
NormativaChunkRepository sin cambios).

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

from app.domain.entities.rag import NormativaChunk


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
    # nada rio abajo (rag_retrieval.py, los casos de uso) lee esos campos de un
    # NormativaChunk (ver docs/saturdays_ai/00-plan.md).
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
