"""create cases table

Revision ID: 0001_create_cases
Revises:
Create Date: 2026-05-16 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_create_cases"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order", sa.Integer(), nullable=False),
        sa.Column("emoji", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("type", sa.String(length=80), nullable=False),
        sa.Column("task", sa.Text(), nullable=False),
        sa.Column("solution", sa.Text(), nullable=False),
        sa.Column("result", sa.Text(), nullable=False),
        sa.Column("stack", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("media_group", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("bot_link", sa.String(length=255), nullable=True),
        sa.Column("extra_link", sa.String(length=255), nullable=True),
        sa.Column("is_visible", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cases_is_visible"), "cases", ["is_visible"], unique=False)
    op.create_index(op.f("ix_cases_order"), "cases", ["order"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cases_order"), table_name="cases")
    op.drop_index(op.f("ix_cases_is_visible"), table_name="cases")
    op.drop_table("cases")

