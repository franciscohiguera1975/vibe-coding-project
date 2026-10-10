from app.domain.entities.rag import NormativaChunk
from app.domain.services.rag_retrieval import cosine_similarity, retrieve_top_k


def _chunk(chunk_id: str, embedding: list[float]) -> NormativaChunk:
    return NormativaChunk(
        chunk_id=chunk_id,
        source_document="doc.pdf",
        article_label=f"Articulo {chunk_id}",
        text=f"texto de {chunk_id}",
        embedding=embedding,
    )


def test_cosine_similarity_is_one_for_identical_vectors():
    assert cosine_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0]) == 1.0


def test_cosine_similarity_is_zero_for_orthogonal_vectors():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_similarity_handles_zero_vectors_without_dividing_by_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0
    assert cosine_similarity([], []) == 0.0


def test_retrieve_top_k_orders_by_similarity_descending():
    query = [1.0, 0.0, 0.0]
    chunks = [
        _chunk("most-similar", [0.9, 0.1, 0.0]),
        _chunk("least-similar", [0.0, 1.0, 0.0]),
        _chunk("middle", [0.5, 0.5, 0.0]),
    ]

    retrieved = retrieve_top_k(query, chunks, k=3)

    assert [r.chunk.chunk_id for r in retrieved] == ["most-similar", "middle", "least-similar"]
    assert retrieved[0].score >= retrieved[1].score >= retrieved[2].score


def test_retrieve_top_k_respects_k_and_ignores_chunks_without_embedding():
    query = [1.0, 0.0]
    chunks = [
        _chunk("a", [1.0, 0.0]),
        _chunk("b", [0.8, 0.2]),
        _chunk("no-embedding", []),
        _chunk("c", [0.0, 1.0]),
    ]

    retrieved = retrieve_top_k(query, chunks, k=2)

    assert len(retrieved) == 2
    assert [r.chunk.chunk_id for r in retrieved] == ["a", "b"]
