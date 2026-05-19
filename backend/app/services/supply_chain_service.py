from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.supply_chain import Supplier, SupplyChainAssessment
from app.schemas.supply_chain import (
    SupplierCreate,
    SupplierUpdate,
    SupplyChainAssessRequest,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import COPILOT_SYSTEM_PROMPT, SUPPLY_CHAIN_PROMPT


async def list_suppliers(db: AsyncSession) -> list[Supplier]:
    return list(
        (await db.execute(select(Supplier).order_by(Supplier.name)))
        .scalars()
        .all()
    )


async def get_supplier(
    db: AsyncSession, supplier_id: uuid.UUID
) -> Optional[Supplier]:
    return (
        await db.execute(select(Supplier).where(Supplier.id == supplier_id))
    ).scalar_one_or_none()


async def create_supplier(db: AsyncSession, payload: SupplierCreate) -> Supplier:
    s = Supplier(**payload.model_dump())
    db.add(s)
    await db.commit()
    await db.refresh(s)
    return s


async def update_supplier(
    db: AsyncSession, s: Supplier, payload: SupplierUpdate
) -> Supplier:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    await db.commit()
    await db.refresh(s)
    return s


async def delete_supplier(db: AsyncSession, s: Supplier) -> None:
    await db.delete(s)
    await db.commit()


async def list_assessments(
    db: AsyncSession, supplier_id: Optional[uuid.UUID] = None
) -> list[SupplyChainAssessment]:
    stmt = select(SupplyChainAssessment).order_by(
        SupplyChainAssessment.created_at.desc()
    )
    if supplier_id is not None:
        stmt = stmt.where(SupplyChainAssessment.supplier_id == supplier_id)
    return list((await db.execute(stmt)).scalars().all())


async def assess_supplier(
    db: AsyncSession,
    supplier: Supplier,
    request: SupplyChainAssessRequest,
    llm: Optional[LLMClient] = None,
) -> SupplyChainAssessment:
    """AI predicts disruption probability + suggests alternative suppliers."""

    llm = llm or get_llm_client()

    prompt = SUPPLY_CHAIN_PROMPT.format(
        name=supplier.name,
        category=supplier.category or "(unspecified)",
        region=supplier.region or "(unspecified)",
        criticality=supplier.criticality,
        description=supplier.description or "(no description)",
        known_alternatives=", ".join(supplier.alternatives) or "(none)",
        additional_context=request.additional_context or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    prob = _clamp(int(result.get("disruption_probability") or 0))

    assessment = SupplyChainAssessment(
        supplier_id=supplier.id,
        disruption_probability=prob,
        risk_drivers=list(result.get("risk_drivers", [])),
        suggested_alternatives=list(result.get("suggested_alternatives", [])),
        summary=str(result.get("summary") or ""),
        details=result,
    )
    supplier.disruption_probability = prob
    db.add(assessment)
    await db.commit()
    await db.refresh(assessment)
    await rag_service.index_supply_chain_assessment(db, assessment)
    return assessment


def _clamp(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, n))
