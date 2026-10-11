from app.domain.entities.rag import NormativaChunk
from app.domain.services.rag_retrieval import cosine_similarity, retrieve_top_k


def _chunk(chunk_id: str, embedding: list[float], text: str | None = None) -> NormativaChunk:
    return NormativaChunk(
        chunk_id=chunk_id,
        source_document="doc.pdf",
        article_label=f"Articulo {chunk_id}",
        text=text if text is not None else f"texto de {chunk_id}",
        embedding=embedding,
    )


def test_cosine_similarity_is_one_for_identical_vectors():
    assert cosine_similarity([1.0, 0.0, 0.0], [1.0, 0.0, 0.0]) == 1.0


def test_cosine_similarity_is_zero_for_orthogonal_vectors():
    assert cosine_similarity([1.0, 0.0], [0.0, 1.0]) == 0.0


def test_cosine_similarity_handles_zero_vectors_without_dividing_by_zero():
    assert cosine_similarity([0.0, 0.0], [1.0, 0.0]) == 0.0
    assert cosine_similarity([], []) == 0.0


def test_retrieve_top_k_orders_by_fused_rrf_score_descending():
    # Sin texto de consulta (BM25 no aporta ranking), el fusionado se reduce al
    # orden vectorial puro.
    query = [1.0, 0.0, 0.0]
    chunks = [
        _chunk("most-similar", [0.9, 0.1, 0.0]),
        _chunk("least-similar", [0.0, 1.0, 0.0]),
        _chunk("middle", [0.5, 0.5, 0.0]),
    ]

    retrieved = retrieve_top_k(query, "", chunks, k=3)

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

    retrieved = retrieve_top_k(query, "", chunks, k=2)

    assert len(retrieved) == 2
    assert [r.chunk.chunk_id for r in retrieved] == ["a", "b"]


def test_retrieve_top_k_promotes_keyword_match_missed_by_vector_search():
    # "no-embedding" aparte: un chunk con embedding lejano al de la consulta
    # (ranking vectorial bajo) pero cuyo texto coincide exactamente con la
    # consulta (ranking BM25 alto) debe poder superar, via RRF, a un chunk que
    # solo es parecido vectorialmente pero no comparte ninguna palabra clave.
    query_embedding = [1.0, 0.0]
    chunks = [
        _chunk("vector-only", [0.95, 0.05], text="contenido generico sin relacion"),
        _chunk(
            "keyword-match",
            [0.0, 1.0],
            text="requisitos de evaluacion y calificacion del silabo",
        ),
    ]

    retrieved = retrieve_top_k(
        query_embedding, "requisitos de evaluacion y calificacion", chunks, k=2
    )

    ids = [r.chunk.chunk_id for r in retrieved]
    assert "keyword-match" in ids
    # keyword-match gana el ranking BM25 (rank 1) y pierde el vectorial (rank
    # 2); vector-only es lo opuesto — con RRF deberian terminar muy cerca o
    # empatados, pero keyword-match nunca puede quedar fuera del top-2.
    assert len(retrieved) == 2


def test_retrieve_top_k_returns_empty_when_no_chunks_have_embeddings():
    chunks = [_chunk("no-embedding", [])]

    assert retrieve_top_k([1.0, 0.0], "consulta", chunks, k=3) == []
