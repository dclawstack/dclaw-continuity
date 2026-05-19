"""P1 features: exercises, crisis activations, vendors, communications

Revision ID: 0002_p1_features
Revises: 0001_initial_p0
Create Date: 2026-05-18

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_p1_features"
down_revision = "0001_initial_p0"
branch_labels = None
depends_on = None


def upgrade() -> None:
    exercise_status = sa.Enum(
        "planned", "running", "completed", "cancelled", name="exercise_status"
    )
    activation_status = sa.Enum(
        "activated", "recovering", "stabilized", "closed", name="activation_status"
    )

    op.create_table(
        "exercises",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "bcp_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bcps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("scenario", sa.Text(), nullable=False),
        sa.Column(
            "objectives",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "status", exercise_status, nullable=False, server_default="planned"
        ),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "evaluation",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_exercises_bcp_id", "exercises", ["bcp_id"])

    op.create_table(
        "crisis_activations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "bcp_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("bcps.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_crisis_id", sa.String(255), nullable=True),
        sa.Column("source", sa.String(64), nullable=False, server_default="manual"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "status",
            activation_status,
            nullable=False,
            server_default="activated",
        ),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("closed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "timeline",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_crisis_activations_bcp_id", "crisis_activations", ["bcp_id"]
    )
    op.create_index(
        "ix_crisis_activations_external_crisis_id",
        "crisis_activations",
        ["external_crisis_id"],
    )

    op.create_table(
        "vendors",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("contact", sa.String(255), nullable=False, server_default=""),
        sa.Column(
            "services_provided", sa.Text(), nullable=False, server_default=""
        ),
        sa.Column("tier", sa.String(32), nullable=False, server_default="tier-2"),
        sa.Column(
            "readiness_score", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "vendor_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "vendor_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("vendors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "readiness_score", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "risk_level", sa.String(32), nullable=False, server_default="medium"
        ),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
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
        "ix_vendor_assessments_vendor_id", "vendor_assessments", ["vendor_id"]
    )

    op.create_table(
        "communication_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("audience", sa.String(255), nullable=False),
        sa.Column("scenario", sa.String(255), nullable=False),
        sa.Column("tone", sa.String(64), nullable=False, server_default="formal"),
        sa.Column(
            "channels",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "escalation_path",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_communication_plans_function_id",
        "communication_plans",
        ["function_id"],
    )

    op.create_table(
        "communication_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "plan_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("communication_plans.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("channel", sa.String(64), nullable=False),
        sa.Column("trigger", sa.String(255), nullable=False, server_default=""),
        sa.Column("subject", sa.String(255), nullable=False, server_default=""),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_communication_templates_plan_id",
        "communication_templates",
        ["plan_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_communication_templates_plan_id", table_name="communication_templates"
    )
    op.drop_table("communication_templates")

    op.drop_index(
        "ix_communication_plans_function_id", table_name="communication_plans"
    )
    op.drop_table("communication_plans")

    op.drop_index(
        "ix_vendor_assessments_vendor_id", table_name="vendor_assessments"
    )
    op.drop_table("vendor_assessments")

    op.drop_table("vendors")

    op.drop_index(
        "ix_crisis_activations_external_crisis_id", table_name="crisis_activations"
    )
    op.drop_index("ix_crisis_activations_bcp_id", table_name="crisis_activations")
    op.drop_table("crisis_activations")

    op.drop_index("ix_exercises_bcp_id", table_name="exercises")
    op.drop_table("exercises")

    for name in ("activation_status", "exercise_status"):
        op.execute(f"DROP TYPE IF EXISTS {name}")
