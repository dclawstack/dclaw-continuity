from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vendor import Vendor, VendorAssessment
from app.schemas.vendor import VendorAssessRequest, VendorCreate, VendorUpdate
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, VENDOR_CONTINUITY_PROMPT


async def list_vendors(db: AsyncSession) -> list[Vendor]:
    result = await db.execute(select(Vendor).order_by(Vendor.name))
    return list(result.scalars().all())


async def get_vendor(db: AsyncSession, vendor_id: uuid.UUID) -> Optional[Vendor]:
    result = await db.execute(select(Vendor).where(Vendor.id == vendor_id))
    return result.scalar_one_or_none()


async def create_vendor(db: AsyncSession, payload: VendorCreate) -> Vendor:
    v = Vendor(**payload.model_dump())
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v


async def update_vendor(db: AsyncSession, v: Vendor, payload: VendorUpdate) -> Vendor:
    for k, val in payload.model_dump(exclude_unset=True).items():
        setattr(v, k, val)
    await db.commit()
    await db.refresh(v)
    return v


async def delete_vendor(db: AsyncSession, v: Vendor) -> None:
    await db.delete(v)
    await db.commit()


async def list_assessments(
    db: AsyncSession, vendor_id: Optional[uuid.UUID] = None
) -> list[VendorAssessment]:
    stmt = select(VendorAssessment).order_by(VendorAssessment.created_at.desc())
    if vendor_id is not None:
        stmt = stmt.where(VendorAssessment.vendor_id == vendor_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def assess_vendor(
    db: AsyncSession,
    vendor: Vendor,
    request: VendorAssessRequest,
    llm: Optional[LLMClient] = None,
) -> VendorAssessment:
    """Run AI continuity scoring against the vendor and persist a new assessment."""

    llm = llm or get_llm_client()

    prompt = VENDOR_CONTINUITY_PROMPT.format(
        name=vendor.name,
        description=vendor.description or "(no description)",
        services=vendor.services_provided or "(unspecified)",
        tier=vendor.tier,
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    score = _clamp(int(result.get("readiness_score") or 0))
    risk = str(result.get("risk_level") or "medium")

    assessment = VendorAssessment(
        vendor_id=vendor.id,
        readiness_score=score,
        risk_level=risk,
        summary=result.get("summary", ""),
        details=result,
    )
    vendor.readiness_score = score
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    await rag_service.index_vendor_assessment(db, assessment)
    return assessment


def _clamp(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, n))
