"""drop normativa_chunks table (moved to lancedb)

Revision ID: 73b590c68190
Revises: b4d2e8a1f6c3
Create Date: 2026-10-09 14:35:31.417604

Cambio de arquitectura (ver docs/saturdays_ai/00-plan.md §5): los chunks +
embeddings de la normativa dejan de vivir en Postgres (JSONB + fuerza bruta en
Python) y pasan a una tabla LanceDB embebida, co-ubicada con el proceso del
backend (decision pedagogica deliberada, no una necesidad de escala — ver el
plan para el razonamiento completo). `rag_evaluation_runs` NO se toca: los
resultados de evaluacion baseline-vs-RAG se quedan en Postgres.

`downgrade()` recrea la tabla con el mismo esquema que la migracion original
(b4d2e8a1f6c3) mas no repuebla datos: si se hace rollback, hay que volver a
correr scripts/rag/load_chunks.py apuntando a Postgres de nuevo tras revertir
tambien el codigo de la capa de infraestructura.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "73b590c68190"
down_revision: str | None = "b4d2e8a1f6c3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.drop_index(op.f("ix_normativa_chunks_chunk_id"), table_name="normativa_chunks")
    op.drop_table("normativa_chunks")


def downgrade() -> None:
    op.create_table(
        "normativa_chunks",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("chunk_id", sa.String(length=50), nullable=False),
        sa.Column("source_document", sa.String(length=255), nullable=False),
        sa.Column("article_label", sa.String(length=100), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_normativa_chunks")),
        sa.UniqueConstraint("chunk_id", name=op.f("uq_normativa_chunks_chunk_id")),
    )
    op.create_index(
        op.f("ix_normativa_chunks_chunk_id"), "normativa_chunks", ["chunk_id"], unique=True
    )
