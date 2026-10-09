"""add practice narrations

Revision ID: a3c1f9b2d7e4
Revises: 7f5c9ed4610b
Create Date: 2026-10-08 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a3c1f9b2d7e4"
down_revision: str | None = "7f5c9ed4610b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "practice_narrations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("practice_id", sa.UUID(), nullable=False),
        sa.Column("lang", sa.String(length=5), nullable=False),
        sa.Column("storage_key", sa.String(length=255), nullable=False),
        sa.Column("text_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["practice_id"],
            ["practices.id"],
            name=op.f("fk_practice_narrations_practice_id_practices"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_practice_narrations")),
        sa.UniqueConstraint(
            "practice_id", "lang", name="uq_practice_narrations_practice_lang"
        ),
    )


def downgrade() -> None:
    op.drop_table("practice_narrations")
