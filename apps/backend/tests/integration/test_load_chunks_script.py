import importlib.util
import json
from pathlib import Path

from app.infrastructure.ai.mock_rag_adapter import MockRagAdapter
from app.infrastructure.database.unit_of_work import SqlAlchemyUnitOfWork

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
LOAD_CHUNKS_SCRIPT = BACKEND_DIR / "scripts" / "rag" / "load_chunks.py"


def _import_load_chunks():
    # scripts/ no es un paquete (sin __init__.py, igual que scripts/seed.py) —
    # se importa por ruta de archivo para llamar load_chunks() directamente y
    # poder pasarle un EmbeddingPort espia, en vez de correrlo como subprocess.
    spec = importlib.util.spec_from_file_location("rag_load_chunks_module", LOAD_CHUNKS_SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _CountingEmbeddingPort:
    """Envoltorio sobre MockRagAdapter que cuenta cuantas veces se llamo a
    embed() — mismo estilo que la prueba de idempotencia de la narracion
    (GeneratePracticeNarrationUseCase), que compara un hash para no volver a
    llamar al proveedor externo si el texto fuente no cambio."""

    def __init__(self) -> None:
        self._inner = MockRagAdapter()
        self.call_count = 0

    def embed(self, text: str) -> list[float]:
        self.call_count += 1
        return self._inner.embed(text)


def test_load_chunks_is_idempotent_and_skips_already_embedded_chunks(tmp_path):
    module = _import_load_chunks()

    records = [
        {
            "chunk_id": "idempotency-0001",
            "source_document": "doc-prueba.pdf",
            "article_label": "Articulo 1",
            "text": "Primer fragmento de prueba.",
        },
        {
            "chunk_id": "idempotency-0002",
            "source_document": "doc-prueba.pdf",
            "article_label": "Articulo 2",
            "text": "Segundo fragmento de prueba.",
        },
    ]
    input_path = tmp_path / "chunks.jsonl"
    input_path.write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records), encoding="utf-8"
    )

    embedding_port = _CountingEmbeddingPort()

    first_run = module.load_chunks(input_path, embedding_port=embedding_port)
    assert first_run == {"embedded": 2, "skipped": 0, "total": 2}
    assert embedding_port.call_count == 2

    second_run = module.load_chunks(input_path, embedding_port=embedding_port)
    assert second_run == {"embedded": 0, "skipped": 2, "total": 2}
    # El segundo pase no debe volver a llamar embed() para chunks que ya tienen
    # un embedding no nulo guardado — el contador no debe crecer.
    assert embedding_port.call_count == 2

    with SqlAlchemyUnitOfWork() as uow:
        stored = uow.normativa_chunks.get_by_chunk_id("idempotency-0001")
        assert stored is not None
        assert stored.embedding
