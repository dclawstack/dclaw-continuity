from fastapi import APIRouter
from datetime import datetime
from uuid import uuid4
import random
from dclaw_continuity.models import BusinessContinuityPlan, BcpCreate

router = APIRouter()

@router.post("/plans", response_model=BusinessContinuityPlan)
async def create_item(payload: BcpCreate):
    return BusinessContinuityPlan(
        id=str(uuid4()),
        business_unit=payload.business_unit,
        impact_level=payload.impact_level,
        rto_hours=random.randint(1, 72),
        rpo_hours=random.randint(1, 24),
        backup_sites=["Site B - Denver", "Site C - Austin"],
        recovery_status="tested",
        created_at=datetime.utcnow(),
    )

@router.get("/plans/{plan_id}/drills")
async def get_item(plan_id: str):
    return [{"date": "2025-01-15", "result": "Passed"}, {"date": "2025-04-10", "result": "Passed"}, {"date": "2025-07-20", "result": "Scheduled"}]
