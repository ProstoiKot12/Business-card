"""rename case fields: solution→approach, result→outcome, add context

Revision ID: 0002_rename_case_fields
Revises: 0001_create_cases
Create Date: 2026-06-10 00:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002_rename_case_fields"
down_revision: str | None = "0001_create_cases"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column("cases", "solution", new_column_name="approach")
    op.alter_column("cases", "result", new_column_name="outcome")
    op.add_column("cases", sa.Column("context", sa.String(length=120), nullable=False, server_default=""))


def downgrade() -> None:
    op.drop_column("cases", "context")
    op.alter_column("cases", "outcome", new_column_name="result")
    op.alter_column("cases", "approach", new_column_name="solution")