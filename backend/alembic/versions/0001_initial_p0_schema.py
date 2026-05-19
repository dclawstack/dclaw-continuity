"""initial P0 schema: business functions, BCPs, dependencies, impact, recovery, copilot

Revision ID: 0001_initial_p0
Revises:
Create Date: 2026-05-18

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_initial_p0"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    criticality = sa.Enum(
        "low", "medium", "high", "critical", name="criticality"
    )
    bcp_status = sa.Enum("draft", "review", "approved", "retired", name="bcp_status")
    dependency_type = sa.Enum(
        "system",
        "process",
        "people",
        "vendor",
        "facility",
        "data",
        name="dependency_type",
    )
    strategy_kind = sa.Enum(
        "hot_site",
        "warm_site",
        "cold_site",
        "remote_work",
        "third_party",
        "manual_workaround",
        "redundancy",
        "other",
        name="strategy_kind",
    )

    op.create_table(
        "business_functions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("owner", sa.String(255), nullable=False, server_default=""),
        sa.Column("criticality", criticality, nullable=False, server_default="medium"),
        sa.Column("rto_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rpo_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "bcps",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", bcp_status, nullable=False, server_default="draft"),
        sa.Column(
            "content",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "gaps",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_bcps_function_id", "bcps", ["function_id"])

    op.create_table(
        "dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "depends_on_function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("type", dependency_type, nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("criticality", sa.String(32), nullable=False, server_default="medium"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_dependencies_function_id", "dependencies", ["function_id"])

    op.create_table(
        "impact_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("scenario", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "revenue_impact_usd", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "operational_impact_score",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "reputation_impact_score",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "details",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_impact_assessments_function_id",
        "impact_assessments",
        ["function_id"],
    )

    op.create_table(
        "recovery_strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("kind", strategy_kind, nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "estimated_cost_usd", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("rto_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rpo_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "is_recommended",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "details",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_recovery_strategies_function_id",
        "recovery_strategies",
        ["function_id"],
    )

    op.create_table(
        "copilot_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "conversation_id", postgresql.UUID(as_uuid=True), nullable=False
        ),
        sa.Column("user_sub", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "suggestions",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_copilot_messages_conversation_id",
        "copilot_messages",
        ["conversation_id"],
    )
    op.create_index(
        "ix_copilot_messages_user_sub", "copilot_messages", ["user_sub"]
    )


def downgrade() -> None:
    op.drop_index("ix_copilot_messages_user_sub", table_name="copilot_messages")
    op.drop_index(
        "ix_copilot_messages_conversation_id", table_name="copilot_messages"
    )
    op.drop_table("copilot_messages")

    op.drop_index(
        "ix_recovery_strategies_function_id", table_name="recovery_strategies"
    )
    op.drop_table("recovery_strategies")

    op.drop_index(
        "ix_impact_assessments_function_id", table_name="impact_assessments"
    )
    op.drop_table("impact_assessments")

    op.drop_index("ix_dependencies_function_id", table_name="dependencies")
    op.drop_table("dependencies")

    op.drop_index("ix_bcps_function_id", table_name="bcps")
    op.drop_table("bcps")

    op.drop_table("business_functions")

    for name in (
        "strategy_kind",
        "dependency_type",
        "bcp_status",
        "criticality",
    ):
        op.execute(f"DROP TYPE IF EXISTS {name}")
