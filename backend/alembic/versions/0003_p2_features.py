"""P2 features: work area, IT DR, supply chain, regulatory reports

Revision ID: 0003_p2_features
Revises: 0002_p1_features
Create Date: 2026-05-18

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_p2_features"
down_revision = "0002_p1_features"
branch_labels = None
depends_on = None


def upgrade() -> None:
    site_kind = sa.Enum(
        "alternate_office",
        "remote",
        "hot_site",
        "warm_site",
        "cold_site",
        "coworking",
        "other",
        name="site_kind",
    )
    system_tier = sa.Enum(
        "tier-0", "tier-1", "tier-2", "tier-3", name="system_tier"
    )
    report_status = sa.Enum(
        "draft", "validated", "submitted", "rejected", name="report_status"
    )

    op.create_table(
        "work_area_sites",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("kind", site_kind, nullable=False),
        sa.Column("location", sa.String(255), nullable=False, server_default=""),
        sa.Column(
            "capacity_seats", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "has_remote_access",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "work_area_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "function_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("business_functions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "headcount_required", sa.Integer(), nullable=False, server_default="0"
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
        "ix_work_area_plans_function_id", "work_area_plans", ["function_id"]
    )

    op.create_table(
        "it_systems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("owner", sa.String(255), nullable=False, server_default=""),
        sa.Column("tier", system_tier, nullable=False, server_default="tier-2"),
        sa.Column("rto_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("rpo_minutes", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "backup_strategy", sa.String(255), nullable=False, server_default=""
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "it_dr_plans",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "system_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("it_systems.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "procedure",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "test_plan",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_test_passed", sa.Boolean(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_it_dr_plans_system_id", "it_dr_plans", ["system_id"])

    op.create_table(
        "suppliers",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("category", sa.String(128), nullable=False, server_default=""),
        sa.Column("region", sa.String(128), nullable=False, server_default=""),
        sa.Column(
            "criticality", sa.String(32), nullable=False, server_default="medium"
        ),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column(
            "alternatives",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "disruption_probability",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "supply_chain_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "supplier_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("suppliers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "disruption_probability",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "risk_drivers",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
        ),
        sa.Column(
            "suggested_alternatives",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'[]'::jsonb"),
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
        "ix_supply_chain_assessments_supplier_id",
        "supply_chain_assessments",
        ["supplier_id"],
    )

    op.create_table(
        "regulatory_reports",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("framework", sa.String(64), nullable=False),
        sa.Column("period", sa.String(64), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column(
            "status", report_status, nullable=False, server_default="draft"
        ),
        sa.Column(
            "content",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "validation",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "submission_reference",
            sa.String(255),
            nullable=False,
            server_default="",
        ),
        sa.Column("notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("regulatory_reports")
    op.drop_index(
        "ix_supply_chain_assessments_supplier_id",
        table_name="supply_chain_assessments",
    )
    op.drop_table("supply_chain_assessments")
    op.drop_table("suppliers")
    op.drop_index("ix_it_dr_plans_system_id", table_name="it_dr_plans")
    op.drop_table("it_dr_plans")
    op.drop_table("it_systems")
    op.drop_index("ix_work_area_plans_function_id", table_name="work_area_plans")
    op.drop_table("work_area_plans")
    op.drop_table("work_area_sites")

    for name in ("report_status", "system_tier", "site_kind"):
        op.execute(f"DROP TYPE IF EXISTS {name}")
