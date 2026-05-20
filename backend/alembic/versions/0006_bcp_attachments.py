"""bcp attachments column

Revision ID: 0006_bcp_attachments
Revises: 0005_users
Create Date: 2026-05-20

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_bcp_attachments"
down_revision = "0005_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "bcps",
        sa.Column(
            "attachments",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
    )


def downgrade() -> None:
    op.drop_column("bcps", "attachments")
