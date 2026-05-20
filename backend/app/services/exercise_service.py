from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bcp import BCP
from app.models.business_function import BusinessFunction
from app.models.exercise import Exercise, ExerciseStatus
from app.schemas.exercise import (
    ExerciseCreate,
    ExerciseRunObservation,
    ExerciseUpdate,
)
from app.services import rag_service
from app.services.llm import ChatMessage, LLMClient, get_llm_client
from app.services.prompts import (
    COPILOT_SYSTEM_PROMPT,
    EXERCISE_EVALUATION_PROMPT,
    EXERCISE_SCENARIO_PROMPT,
)


async def list_exercises(
    db: AsyncSession, bcp_id: Optional[uuid.UUID] = None
) -> list[Exercise]:
    stmt = select(Exercise).order_by(Exercise.created_at.desc())
    if bcp_id is not None:
        stmt = stmt.where(Exercise.bcp_id == bcp_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_exercise(db: AsyncSession, exercise_id: uuid.UUID) -> Optional[Exercise]:
    result = await db.execute(select(Exercise).where(Exercise.id == exercise_id))
    return result.scalar_one_or_none()


async def create_exercise(db: AsyncSession, payload: ExerciseCreate) -> Exercise:
    ex = Exercise(**payload.model_dump())
    db.add(ex)
    await db.commit()
    await db.refresh(ex)
    return ex


async def update_exercise(
    db: AsyncSession, ex: Exercise, payload: ExerciseUpdate
) -> Exercise:
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(ex, k, v)
    await db.commit()
    await db.refresh(ex)
    return ex


async def delete_exercise(db: AsyncSession, ex: Exercise) -> None:
    await db.delete(ex)
    await db.commit()


async def generate_exercise_from_bcp(
    db: AsyncSession,
    bcp: BCP,
    focus: str = "",
    llm: Optional[LLMClient] = None,
) -> Exercise:
    """Ask the AI to draft a realistic exercise scenario for a BCP."""

    llm = llm or get_llm_client()
    fn = (
        await db.execute(
            select(BusinessFunction).where(BusinessFunction.id == bcp.function_id)
        )
    ).scalar_one()

    prompt = EXERCISE_SCENARIO_PROMPT.format(
        function_name=fn.name,
        criticality=fn.criticality.value,
        bcp_title=bcp.title,
        bcp_summary=bcp.summary or "(none)",
        focus=focus or "general readiness",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    ex = Exercise(
        bcp_id=bcp.id,
        name=result.get("name") or f"Exercise — {bcp.title}",
        scenario=result.get("scenario", ""),
        objectives=result.get("objectives", []),
        status=ExerciseStatus.PLANNED,
    )
    db.add(ex)
    await db.commit()
    await db.refresh(ex)
    return ex


async def start_exercise(db: AsyncSession, ex: Exercise) -> Exercise:
    if ex.status != ExerciseStatus.PLANNED:
        return ex
    ex.status = ExerciseStatus.RUNNING
    ex.started_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ex)
    return ex


async def evaluate_exercise(
    db: AsyncSession,
    ex: Exercise,
    observation: ExerciseRunObservation,
    llm: Optional[LLMClient] = None,
) -> Exercise:
    """Run AI evaluation of how well the BCP was executed and persist a score."""

    llm = llm or get_llm_client()
    bcp = (await db.execute(select(BCP).where(BCP.id == ex.bcp_id))).scalar_one()

    prompt = EXERCISE_EVALUATION_PROMPT.format(
        exercise_name=ex.name,
        scenario=ex.scenario,
        objectives=", ".join(ex.objectives) or "(none recorded)",
        observations=observation.observations,
        issues=", ".join(observation.issues_encountered) or "(none reported)",
        bcp_summary=bcp.summary or "(none)",
    )
    result = await llm.chat_json(
        [
            ChatMessage(role="system", content=COPILOT_SYSTEM_PROMPT),
            ChatMessage(role="user", content=prompt),
        ]
    )

    ex.score = _clamp_score(int(result.get("score") or 0))
    ex.evaluation = result
    ex.status = ExerciseStatus.COMPLETED
    ex.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(ex)
    await rag_service.index_exercise_evaluation(db, ex)
    return ex


def _clamp_score(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, n))
