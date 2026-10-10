"""Extrae y trocea (chunk) la normativa de docs/reglamentos_ute/ en unidades por
articulo, listas para generar embeddings (ver docs/saturdays_ai/02-hpc-pasos.md,
Job A). No depende de ningun framework de RAG: cada chunk es un articulo completo
(no se parte un articulo a la mitad), con metadatos suficientes para citar la
fuente exacta en una respuesta.

Patrones de encabezado de articulo soportados: "Articulo N.- ..." y "Art. N.- ...".
Los documentos sin esa estructura (instructivos cortos) se trocean por parrafo.

Uso:
    python3 scripts/rag/ingest_normativa.py \
        --input-dir ../../docs/reglamentos_ute \
        --output chunks.jsonl
"""

import argparse
import json
import re
import subprocess
from pathlib import Path

ARTICLE_PATTERN = re.compile(r"^(Art(?:ículo|\.)\s*\d+)[.\-\s]", re.MULTILINE)
MIN_CHUNK_CHARS = 40
MAX_CHUNK_CHARS = 4000


def extract_text(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def split_by_article(text: str) -> list[tuple[str, str]]:
    """Devuelve [(etiqueta_articulo, texto_del_articulo), ...]. Si el documento no
    tiene marcas de articulo reconocibles, devuelve una lista vacia (el llamador
    debe usar el fallback por parrafo)."""
    matches = list(ARTICLE_PATTERN.finditer(text))
    if not matches:
        return []
    chunks = []
    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        label = match.group(1).strip()
        body = text[start:end].strip()
        if len(body) >= MIN_CHUNK_CHARS:
            chunks.append((label, body[:MAX_CHUNK_CHARS]))
    return chunks


def split_by_paragraph(text: str) -> list[tuple[str, str]]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    for i, para in enumerate(paragraphs):
        if len(para) >= MIN_CHUNK_CHARS:
            chunks.append((f"parrafo {i + 1}", para[:MAX_CHUNK_CHARS]))
    return chunks


def ingest_document(pdf_path: Path, doc_id: int) -> list[dict]:
    text = extract_text(pdf_path)
    article_chunks = split_by_article(text)
    chunks = article_chunks if article_chunks else split_by_paragraph(text)

    records = []
    for i, (label, body) in enumerate(chunks):
        records.append(
            {
                "chunk_id": f"doc{doc_id}-{i:04d}",
                "source_document": pdf_path.name,
                "article_label": label,
                "text": body,
            }
        )
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    pdf_paths = sorted(args.input_dir.glob("*.pdf"))
    if not pdf_paths:
        raise SystemExit(f"No se encontraron PDFs en {args.input_dir}")

    all_records = []
    for doc_id, pdf_path in enumerate(pdf_paths):
        records = ingest_document(pdf_path, doc_id)
        print(f"{pdf_path.name}: {len(records)} chunks")
        all_records.extend(records)

    with open(args.output, "w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"\nTotal: {len(all_records)} chunks -> {args.output}")


if __name__ == "__main__":
    main()
