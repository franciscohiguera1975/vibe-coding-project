"""add rag tables (normativa_chunks, rag_evaluation_runs)

Revision ID: b4d2e8a1f6c3
Revises: a3c1f9b2d7e4
Create Date: 2026-10-09 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4d2e8a1f6c3"
down_revision: str | None = "a3c1f9b2d7e4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
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

    op.create_table(
        "rag_evaluation_runs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("results", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("summary", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_rag_evaluation_runs")),
    )


def downgrade() -> None:
    op.drop_table("rag_evaluation_runs")
    op.drop_index(op.f("ix_normativa_chunks_chunk_id"), table_name="normativa_chunks")
    op.drop_table("normativa_chunks")
