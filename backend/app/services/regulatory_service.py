from __future__ import annotations

import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bcp import BCP
from app.models.business_function import BusinessFunction
from app.models.exercise import Exercise
from app.models.impact_assessment import ImpactAssessment
from app.models.recovery_strategy import RecoveryStrategy
from app.models.regulatory import RegulatoryReport, ReportStatus
from app.models.vendor import Vendor
from app.schemas.regulatory import (
    RegulatoryReportGenerateRequest,
    RegulatoryReportSubmitRequest,
    RegulatoryReportUpdate,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, REGULATORY_REPORT_PROMPT


async def list_reports(db: AsyncSession) -> list[RegulatoryReport]:
    return list(
        (await db.execute(select(RegulatoryReport).order_by(RegulatoryReport.created_at.desc())))
        .scalars()
        .all()
    )


async def get_report(db: AsyncSession, report_id: uuid.UUID) -> RegulatoryReport | None:
    return (
        await db.execute(select(RegulatoryReport).where(RegulatoryReport.id == report_id))
    ).scalar_one_or_none()


async def update_report(
    db: AsyncSession, report: RegulatoryReport, payload: RegulatoryReportUpdate
) -> RegulatoryReport:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(report, k, v)
    await db.commit()
    await db.refresh(report)
    return report


async def delete_report(db: AsyncSession, report: RegulatoryReport) -> None:
    await db.delete(report)
    await db.commit()


async def generate_report(
    db: AsyncSession,
    request: RegulatoryReportGenerateRequest,
    llm: LLMClient | None = None,
) -> RegulatoryReport:
    """Auto-populate a regulator-facing continuity report from workspace state."""

    llm = llm or get_llm_client()
    snapshot = await _build_evidence_snapshot(db)

    prompt = REGULATORY_REPORT_PROMPT.format(
        framework=request.framework,
        period=request.period,
        snapshot=snapshot,
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    validation = _validate(result)

    report = RegulatoryReport(
        framework=request.framework,
        period=request.period,
        title=str(result.get("title") or f"{request.framework} — {request.period}"),
        status=(ReportStatus.VALIDATED if validation["complete"] else ReportStatus.DRAFT),
        content=result,
        validation=validation,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)
    await rag_service.index_regulatory_report(db, report)
    return report


async def submit_report(
    db: AsyncSession,
    report: RegulatoryReport,
    request: RegulatoryReportSubmitRequest,
) -> RegulatoryReport:
    if report.status not in (ReportStatus.VALIDATED, ReportStatus.DRAFT):
        return report
    if not report.validation.get("complete", False):
        report.status = ReportStatus.REJECTED
        await db.commit()
        await db.refresh(report)
        return report
    report.submission_reference = request.submission_reference
    report.status = ReportStatus.SUBMITTED
    await db.commit()
    await db.refresh(report)
    return report


async def _build_evidence_snapshot(db: AsyncSession) -> dict:
    """Aggregate counts + recent items so the LLM has concrete evidence to cite."""

    fn_count = (await db.execute(select(func.count(BusinessFunction.id)))).scalar() or 0
    bcp_count = (await db.execute(select(func.count(BCP.id)))).scalar() or 0
    ia_count = (await db.execute(select(func.count(ImpactAssessment.id)))).scalar() or 0
    rs_count = (await db.execute(select(func.count(RecoveryStrategy.id)))).scalar() or 0
    ex_count = (await db.execute(select(func.count(Exercise.id)))).scalar() or 0
    vendor_count = (await db.execute(select(func.count(Vendor.id)))).scalar() or 0

    recent_exercises = list(
        (await db.execute(select(Exercise).order_by(Exercise.created_at.desc()).limit(5)))
        .scalars()
        .all()
    )

    return {
        "counts": {
            "business_functions": fn_count,
            "bcps": bcp_count,
            "impact_assessments": ia_count,
            "recovery_strategies": rs_count,
            "exercises_completed": ex_count,
            "vendors_assessed": vendor_count,
        },
        "recent_exercises": [
            {
                "name": e.name,
                "score": e.score,
                "status": e.status.value,
            }
            for e in recent_exercises
        ],
    }


def _validate(content: dict) -> dict:
    """Quick local validation; mark report VALIDATED iff key sections are present."""

    issues: list[str] = []
    if not content.get("executive_summary"):
        issues.append("missing executive_summary")
    sections = content.get("sections") or []
    if not sections:
        issues.append("missing sections")
    elif any(not (s.get("title") and s.get("body")) for s in sections):
        issues.append("section missing title or body")
    if not content.get("metrics"):
        issues.append("missing metrics block")
    return {
        "complete": len(issues) == 0,
        "issues": issues,
        "checked_at": None,  # populated by caller if needed
    }
