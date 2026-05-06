from pydantic import BaseModel
from datetime import datetime
from typing import List

class BusinessContinuityPlan(BaseModel):
    id: str
    business_unit: str
    impact_level: str
    rto_hours: int
    rpo_hours: int
    backup_sites: list[str]
    recovery_status: str
    created_at: datetime

class BcpCreate(BaseModel):
    business_unit: str
    impact_level: str
