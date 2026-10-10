#!/usr/bin/env python
"""Carga chunks.jsonl (ver ingest_normativa.py) en la tabla normativa_chunks,
calculando el embedding de cada fragmento via el EmbeddingPort configurado
(EMBEDDING_PROVIDER=mock por defecto; =tei para el servidor TEI tunelado desde el
HPC, ver docs/saturdays_ai/02-hpc-pasos.md). Idempotente: un chunk que ya tiene un
embedding no nulo en la base se salta (mismo patron que GeneratePracticeNarrationUseCase,
que compara un hash para no recalcular si el texto fuente no cambio) — aqui el chunk_id
es la clave natural estable, asi que basta con mirar si ya existe con embedding.

Uso:
    cd apps/backend && .venv/bin/python scripts/rag/load_chunks.py \
        [--input scripts/rag/data/chunks.jsonl]
"""

import argparse
import json
import sys
import time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
REPO_ROOT = BACKEND_DIR.parent.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(REPO_ROOT))

from app.application.ports.rag import EmbeddingPort  # noqa: E402
from app.domain.entities.rag import NormativaChunk  # noqa: E402
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork  # noqa: E402

DEFAULT_INPUT = Path(__file__).resolve().parent / "data" / "chunks.jsonl"


def _get_embedding_port() -> EmbeddingPort:
    # Reutiliza exactamente la misma seleccion de adaptador que usa la API HTTP
    # (ver app/interfaces/http/dependencies/rag.py), para que el script y la
    # aplicacion siempre calculen embeddings en el mismo espacio vectorial.
    from app.interfaces.http.dependencies.rag import get_embedding_port

    return get_embedding_port()


def load_chunks(input_path: Path, embedding_port: EmbeddingPort | None = None) -> dict[str, int]:
    embedding_port = embedding_port or _get_embedding_port()

    if not input_path.exists():
        raise SystemExit(
            f"No se encontro {input_path}. Ejecute primero scripts/rag/ingest_normativa.py."
        )

    records = []
    with input_path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    skipped = 0
    embedded = 0
    started_at = time.monotonic()

    with SqlAlchemyUnitOfWork() as uow:
        for record in records:
            existing = uow.normativa_chunks.get_by_chunk_id(record["chunk_id"])
            if existing is not None and existing.embedding:
                # Ya tiene embedding calculado: no volver a llamar al proveedor
                # (control de costo/latencia, igual razonamiento que la narracion).
                skipped += 1
                continue

            embedding = embedding_port.embed(record["text"])
            chunk = NormativaChunk(
                chunk_id=record["chunk_id"],
                source_document=record["source_document"],
                article_label=record["article_label"],
                text=record["text"],
                embedding=embedding,
            )
            uow.normativa_chunks.upsert(chunk)
            embedded += 1
        uow.commit()

    elapsed = time.monotonic() - started_at
    print(
        f"normativa_chunks: {embedded} embebidos, {skipped} ya existian "
        f"(total {len(records)}), en {elapsed:.1f}s"
    )
    return {"embedded": embedded, "skipped": skipped, "total": len(records)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    args = parser.parse_args()
    load_chunks(args.input)


if __name__ == "__main__":
    main()
