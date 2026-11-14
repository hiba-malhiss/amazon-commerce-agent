"""add title to threads

Revision ID: a1c4e9d2b7f3
Revises: 8fa4ec671106
Create Date: 2026-11-10

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1c4e9d2b7f3"
down_revision: str | Sequence[str] | None = "8fa4ec671106"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("threads", sa.Column("title", sa.String(length=80), nullable=True))

    # Existing threads are titled from their first user message, spaces collapsed
    op.execute(
        r"""
        UPDATE threads
        SET title = LEFT(regexp_replace(trim(first_message.content), '\s+', ' ', 'g'), 80)
        FROM (
            SELECT DISTINCT ON (thread_id) thread_id, content
            FROM messages
            WHERE role = 'user'
            ORDER BY thread_id, created_at, id
        ) AS first_message
        WHERE first_message.thread_id = threads.id AND threads.title IS NULL
        """
    )


def downgrade() -> None:
    op.drop_column("threads", "title")
