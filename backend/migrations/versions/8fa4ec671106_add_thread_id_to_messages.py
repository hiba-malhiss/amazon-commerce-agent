"""add thread_id to messages

Revision ID: 8fa4ec671106
Revises: bb27a6ca73c2
Create Date: 2026-11-02 15:27:16.568854

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8fa4ec671106"
down_revision: str | Sequence[str] | None = "bb27a6ca73c2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add as nullable first so existing rows can be backfilled
    op.add_column("messages", sa.Column("thread_id", sa.Uuid(), nullable=True))

    # Every message already belongs to an interaction, which knows its thread
    op.execute(
        """
        UPDATE messages
        SET thread_id = interactions.thread_id
        FROM interactions
        WHERE messages.interaction_id = interactions.id
        """
    )

    op.alter_column("messages", "thread_id", nullable=False)
    op.create_foreign_key("messages_thread_id_fkey", "messages", "threads", ["thread_id"], ["id"])
    op.create_index(op.f("ix_messages_thread_id"), "messages", ["thread_id"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_messages_thread_id"), table_name="messages")
    op.drop_constraint("messages_thread_id_fkey", "messages", type_="foreignkey")
    op.drop_column("messages", "thread_id")
