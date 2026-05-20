"""Retrieval-augmented generation over workspace artifacts.

Indexing is **best-effort**: if the embedding backend is unavailable, indexing
silently no-ops and the caller continues. Retrieval likewise returns an empty
list if anything goes wrong, so the Copilot degrades to a non-RAG response.

Each "source" (a BCP, an impact assessment, etc.) may produce one or more
chunks. We re-index by deleting all chunks for a (source_type, source_id) pair
then inserting fresh ones, so updates and re-runs stay consistent.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.models.bcp import BCP
from app.models.business_function import BusinessFunction
from app.models.communication import CommunicationPlan, CommunicationTemplate
from app.models.exercise import Exercise
from app.models.impact_assessment import ImpactAssessment
from app.models.it_dr import ITDRPlan, ITSystem
from app.models.knowledge_chunk import KnowledgeChunk
from app.models.recovery_strategy import RecoveryStrategy
from app.models.regulatory import RegulatoryReport
from app.models.supply_chain import Supplier, SupplyChainAssessment
from app.models.vendor import Vendor, VendorAssessment
from app.models.work_area import WorkAreaPlan
from app.services.embedding import (
    EmbeddingClient,
    EmbeddingUnavailable,
    get_embedding_client,
)

log = get_logger(__name__)


@dataclass(frozen=True)
class Chunk:
    title: str
    text: str


@dataclass(frozen=True)
class SearchHit:
    source_type: str
    source_id: uuid.UUID
    title: str
    text: str
    distance: float


# ── public indexing API ─────────────────────────────────────────────────────


async def index_for_source(
    db: AsyncSession,
    source_type: str,
    source_id: uuid.UUID,
    chunks: list[Chunk],
    embedder: EmbeddingClient | None = None,
) -> int:
    """Replace all chunks for (source_type, source_id) with `chunks`.

    Returns number of chunks indexed (0 if embedding is unavailable).
    """

    if not chunks:
        return 0
    embedder = embedder or get_embedding_client()

    try:
        embeddings = await embedder.embed_batch([c.text for c in chunks])
    except EmbeddingUnavailable as exc:
        log.warning(
            "rag_indexing_skipped",
            source_type=source_type,
            source_id=str(source_id),
            error=str(exc),
        )
        return 0
    except Exception as exc:  # defensive
        log.warning(
            "rag_indexing_failed",
            source_type=source_type,
            source_id=str(source_id),
            error=str(exc),
        )
        return 0

    if len(embeddings) != len(chunks):
        log.warning(
            "rag_embedding_count_mismatch",
            source_type=source_type,
            source_id=str(source_id),
            got=len(embeddings),
            expected=len(chunks),
        )
        return 0

    # Replace existing chunks for this source.
    await db.execute(
        delete(KnowledgeChunk).where(
            KnowledgeChunk.source_type == source_type,
            KnowledgeChunk.source_id == source_id,
        )
    )
    rows = [
        KnowledgeChunk(
            source_type=source_type,
            source_id=source_id,
            title=c.title[:255],
            text=c.text,
            embedding=e,
        )
        for c, e in zip(chunks, embeddings, strict=True)
    ]
    db.add_all(rows)
    await db.commit()
    return len(rows)


async def search(
    db: AsyncSession,
    query: str,
    *,
    k: int | None = None,
    embedder: EmbeddingClient | None = None,
) -> list[SearchHit]:
    """Best-effort cosine-similarity search. Returns [] if embedding fails."""

    if not query.strip():
        return []
    k = k or settings.rag_top_k
    embedder = embedder or get_embedding_client()

    try:
        qvec = await embedder.embed(query)
    except EmbeddingUnavailable as exc:
        log.warning("rag_search_skipped", error=str(exc))
        return []
    except Exception as exc:
        log.warning("rag_search_failed", error=str(exc))
        return []

    distance = KnowledgeChunk.embedding.cosine_distance(qvec)
    stmt = (
        select(
            KnowledgeChunk.source_type,
            KnowledgeChunk.source_id,
            KnowledgeChunk.title,
            KnowledgeChunk.text,
            distance.label("distance"),
        )
        .order_by(distance)
        .limit(k)
    )
    result = await db.execute(stmt)
    return [
        SearchHit(
            source_type=row.source_type,
            source_id=row.source_id,
            title=row.title,
            text=row.text,
            distance=float(row.distance),
        )
        for row in result.all()
    ]


# ── per-source helpers ──────────────────────────────────────────────────────


async def index_bcp(db: AsyncSession, bcp: BCP) -> int:
    fn = (
        await db.execute(select(BusinessFunction).where(BusinessFunction.id == bcp.function_id))
    ).scalar_one()
    text = _stringify_bcp(bcp, fn)
    return await index_for_source(db, "bcp", bcp.id, [Chunk(title=f"BCP: {bcp.title}", text=text)])


async def index_impact(db: AsyncSession, ia: ImpactAssessment) -> int:
    fn = (
        await db.execute(select(BusinessFunction).where(BusinessFunction.id == ia.function_id))
    ).scalar_one()
    text = (
        f"Function: {fn.name} ({fn.criticality.value})\n"
        f"Scenario: {ia.scenario}\n"
        f"Revenue impact: ${ia.revenue_impact_usd}\n"
        f"Ops impact: {ia.operational_impact_score}/10, "
        f"Reputation: {ia.reputation_impact_score}/10\n"
        f"Narrative: {ia.description}"
    )
    return await index_for_source(
        db,
        "impact",
        ia.id,
        [Chunk(title=f"Impact: {ia.scenario}", text=text)],
    )


async def index_recovery_strategy(db: AsyncSession, strat: RecoveryStrategy) -> int:
    fn = (
        await db.execute(select(BusinessFunction).where(BusinessFunction.id == strat.function_id))
    ).scalar_one()
    text = (
        f"Function: {fn.name}\n"
        f"Strategy: {strat.title} ({strat.kind.value})\n"
        f"RTO: {strat.rto_minutes}m / RPO: {strat.rpo_minutes}m\n"
        f"Cost: ${strat.estimated_cost_usd}\n"
        f"Recommended: {strat.is_recommended}\n"
        f"Description: {strat.description}"
    )
    return await index_for_source(
        db,
        "recovery",
        strat.id,
        [Chunk(title=f"Recovery: {strat.title}", text=text)],
    )


async def index_exercise_evaluation(db: AsyncSession, ex: Exercise) -> int:
    if not ex.evaluation:
        return 0
    ev = ex.evaluation
    text = (
        f"Exercise: {ex.name}\n"
        f"Score: {ex.score}/100\n"
        f"Strengths: {ev.get('strengths', [])}\n"
        f"Weaknesses: {ev.get('weaknesses', [])}\n"
        f"Recommendations: {ev.get('recommendations', [])}\n"
        f"Observations baseline scenario: {ex.scenario}"
    )
    return await index_for_source(
        db,
        "exercise_eval",
        ex.id,
        [Chunk(title=f"Exercise eval: {ex.name}", text=text)],
    )


async def index_vendor_assessment(db: AsyncSession, assessment: VendorAssessment) -> int:
    vendor = (
        await db.execute(select(Vendor).where(Vendor.id == assessment.vendor_id))
    ).scalar_one()
    text = (
        f"Vendor: {vendor.name} ({vendor.tier})\n"
        f"Services: {vendor.services_provided}\n"
        f"Readiness: {assessment.readiness_score}/100, "
        f"Risk: {assessment.risk_level}\n"
        f"Summary: {assessment.summary}"
    )
    return await index_for_source(
        db,
        "vendor_assessment",
        assessment.id,
        [Chunk(title=f"Vendor: {vendor.name}", text=text)],
    )


async def index_communication_plan(db: AsyncSession, plan: CommunicationPlan) -> int:
    """One chunk per template body, plus a summary chunk."""

    templates = (
        (
            await db.execute(
                select(CommunicationTemplate).where(CommunicationTemplate.plan_id == plan.id)
            )
        )
        .scalars()
        .all()
    )

    chunks: list[Chunk] = [
        Chunk(
            title=f"Comms plan: {plan.audience} — {plan.scenario}",
            text=(
                f"Audience: {plan.audience}\n"
                f"Scenario: {plan.scenario}\n"
                f"Tone: {plan.tone}\n"
                f"Channels: {plan.channels}\n"
                f"Escalation: {plan.escalation_path}"
            ),
        )
    ]
    for t in templates:
        chunks.append(
            Chunk(
                title=f"Comms template [{t.channel}]: {t.subject or plan.scenario}",
                text=f"Channel: {t.channel}\nTrigger: {t.trigger}\nSubject: {t.subject}\nBody: {t.body}",
            )
        )
    return await index_for_source(db, "communication_plan", plan.id, chunks)


async def index_it_dr_plan(db: AsyncSession, plan: ITDRPlan) -> int:
    sys = (await db.execute(select(ITSystem).where(ITSystem.id == plan.system_id))).scalar_one()
    text = (
        f"System: {sys.name} ({sys.tier.value})\n"
        f"RTO: {sys.rto_minutes}m / RPO: {sys.rpo_minutes}m\n"
        f"Backup: {sys.backup_strategy}\n"
        f"Plan title: {plan.title}\n"
        f"Summary: {plan.summary}\n"
        f"Procedure: {plan.procedure}\n"
        f"Test plan: {plan.test_plan}"
    )
    return await index_for_source(
        db, "it_dr_plan", plan.id, [Chunk(title=f"IT DR: {plan.title}", text=text)]
    )


async def index_supply_chain_assessment(db: AsyncSession, assessment: SupplyChainAssessment) -> int:
    supplier = (
        await db.execute(select(Supplier).where(Supplier.id == assessment.supplier_id))
    ).scalar_one()
    text = (
        f"Supplier: {supplier.name} ({supplier.criticality})\n"
        f"Category: {supplier.category} · Region: {supplier.region}\n"
        f"Disruption probability: {assessment.disruption_probability}%\n"
        f"Risk drivers: {assessment.risk_drivers}\n"
        f"Suggested alternatives: {assessment.suggested_alternatives}\n"
        f"Summary: {assessment.summary}"
    )
    return await index_for_source(
        db,
        "supply_chain_assessment",
        assessment.id,
        [Chunk(title=f"Supply chain: {supplier.name}", text=text)],
    )


async def index_regulatory_report(db: AsyncSession, report: RegulatoryReport) -> int:
    sections = report.content.get("sections") or []
    chunks: list[Chunk] = [
        Chunk(
            title=f"Report: {report.title}",
            text=(
                f"Framework: {report.framework} · Period: {report.period}\n"
                f"Executive summary: {report.content.get('executive_summary', '')}\n"
                f"Metrics: {report.content.get('metrics', {})}"
            ),
        )
    ]
    for s in sections:
        if isinstance(s, dict) and s.get("title") and s.get("body"):
            chunks.append(
                Chunk(
                    title=f"{report.framework} {report.period}: {s['title']}",
                    text=f"Section: {s['title']}\n{s['body']}",
                )
            )
    return await index_for_source(db, "regulatory_report", report.id, chunks)


async def index_work_area_plan(db: AsyncSession, plan: WorkAreaPlan) -> int:
    fn = (
        await db.execute(select(BusinessFunction).where(BusinessFunction.id == plan.function_id))
    ).scalar_one()
    text = (
        f"Function: {fn.name}\n"
        f"Headcount required: {plan.headcount_required}\n"
        f"Summary: {plan.summary}\n"
        f"Details: {plan.details}"
    )
    return await index_for_source(
        db,
        "work_area_plan",
        plan.id,
        [Chunk(title=f"Work area: {fn.name}", text=text)],
    )


def _stringify_bcp(bcp: BCP, fn: BusinessFunction) -> str:
    content = bcp.content or {}
    procedures = content.get("procedures") or []
    steps = "; ".join(
        f"{p.get('step')}. {p.get('action')}" for p in procedures if isinstance(p, dict)
    )
    return (
        f"Function: {fn.name} ({fn.criticality.value})\n"
        f"BCP title: {bcp.title}\n"
        f"Status: {bcp.status.value}\n"
        f"Summary: {bcp.summary}\n"
        f"Objectives: {content.get('objectives', [])}\n"
        f"Activation triggers: {content.get('activation_triggers', [])}\n"
        f"Procedures: {steps}\n"
        f"Recovery targets: {content.get('recovery_targets', {})}"
    )
