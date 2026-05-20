"""RAG: enable pgvector + knowledge_chunks table

Revision ID: 0004_rag_pgvector
Revises: 0003_p2_features
Create Date: 2026-05-18

"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_rag_pgvector"
down_revision = "0003_p2_features"
branch_labels = None
depends_on = None

EMBEDDING_DIM = 768


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "knowledge_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source_type", sa.String(64), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.execute(
        f"ALTER TABLE knowledge_chunks ADD COLUMN embedding vector({EMBEDDING_DIM}) NOT NULL"
    )
    op.create_index(
        "ix_knowledge_chunks_source_type", "knowledge_chunks", ["source_type"]
    )
    op.create_index(
        "ix_knowledge_chunks_source_id", "knowledge_chunks", ["source_id"]
    )
    op.create_index(
        "ix_knowledge_chunks_source_type_id",
        "knowledge_chunks",
        ["source_type", "source_id"],
    )
    # ivfflat or hnsw index for similarity search; ivfflat is broadly available.
    # Note: ivfflat works best after data is loaded — for an empty table this
    # is essentially a stub. Postgres lets us create it anyway.
    op.execute(
        "CREATE INDEX ix_knowledge_chunks_embedding_cosine "
        "ON knowledge_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 50)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_knowledge_chunks_embedding_cosine")
    op.drop_index(
        "ix_knowledge_chunks_source_type_id", table_name="knowledge_chunks"
    )
    op.drop_index("ix_knowledge_chunks_source_id", table_name="knowledge_chunks")
    op.drop_index(
        "ix_knowledge_chunks_source_type", table_name="knowledge_chunks"
    )
    op.drop_table("knowledge_chunks")
    # leave the pgvector extension alone — other schemas might depend on it
