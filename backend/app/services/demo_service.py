"""Demo workspace lifecycle — seed a brand-new tenant + clear it down.

Every visitor who clicks "Seed demo" on the landing page gets a fresh user
with pre-populated continuity content. The `DemoSeed` row remembers exactly
which top-level entities we created so the matching "Clear demo" call wipes
the same set (FK cascades handle everything downstream).
"""

from __future__ import annotations

import secrets
import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.bcp import BCP, BCPStatus
from app.models.business_function import BusinessFunction, Criticality
from app.models.demo import DemoSeed
from app.models.exercise import Exercise, ExerciseStatus
from app.models.impact_assessment import ImpactAssessment
from app.models.recovery_strategy import RecoveryStrategy, StrategyKind
from app.models.user import User
from app.models.vendor import Vendor, VendorAssessment
from app.services import auth_service


async def seed_demo(db: AsyncSession) -> dict:
    """Create a fresh demo user + populate it. Returns dict with credentials,
    a freshly-issued JWT, and metadata for clear()."""

    suffix = secrets.token_hex(4)
    email = f"demo-{suffix}@demo.dclaw.app"
    password = secrets.token_urlsafe(12)

    user = User(
        email=email,
        hashed_password=auth_service.hash_password(password),
        is_demo=True,
    )
    db.add(user)
    await db.flush()  # populate user.id

    function_ids = await _seed_continuity_workspace(db, user)
    vendor_ids = await _seed_vendors(db)

    seed = DemoSeed(
        user_id=user.id,
        created_ids={
            "functions": [str(fid) for fid in function_ids],
            "vendors": [str(vid) for vid in vendor_ids],
        },
    )
    db.add(seed)
    await db.commit()
    await db.refresh(user)

    token, ttl = auth_service.issue_token(user)
    return {
        "user_id": str(user.id),
        "email": email,
        "password": password,
        "access_token": token,
        "expires_in": ttl,
    }


async def clear_demo(db: AsyncSession, user_id: uuid.UUID) -> bool:
    """Tear down a previously-seeded demo. Returns True if anything was deleted."""

    user = (
        await db.execute(
            select(User).where(User.id == user_id, User.is_demo.is_(True))
        )
    ).scalar_one_or_none()
    if user is None:
        return False

    seed = (
        await db.execute(
            select(DemoSeed).where(DemoSeed.user_id == user.id)
        )
    ).scalar_one_or_none()

    if seed is not None:
        fn_ids = [uuid.UUID(s) for s in seed.created_ids.get("functions", [])]
        vendor_ids = [uuid.UUID(s) for s in seed.created_ids.get("vendors", [])]

        # Cascade fans out: deleting a function drops its BCP/impact/recovery/
        # exercise/comms/work-area rows. Deleting a vendor drops its assessments.
        if fn_ids:
            await db.execute(
                delete(BusinessFunction).where(BusinessFunction.id.in_(fn_ids))
            )
        if vendor_ids:
            await db.execute(delete(Vendor).where(Vendor.id.in_(vendor_ids)))

    # Deleting the user cascades the DemoSeed row.
    await db.delete(user)
    await db.commit()
    return True


# ── private: the actual sample content ──────────────────────────────────────


async def _seed_continuity_workspace(
    db: AsyncSession, user: User
) -> list[uuid.UUID]:
    payments = BusinessFunction(
        name=f"Payments [{user.email}]",
        description="Card processing for ecommerce — every transaction flows through here.",
        owner=user.email,
        criticality=Criticality.CRITICAL,
        rto_minutes=60,
        rpo_minutes=15,
    )
    checkout = BusinessFunction(
        name=f"Online Checkout [{user.email}]",
        description="Cart, address selection, and order placement.",
        owner=user.email,
        criticality=Criticality.CRITICAL,
        rto_minutes=30,
        rpo_minutes=5,
    )
    support = BusinessFunction(
        name=f"Customer Support [{user.email}]",
        description="Tier-1 + tier-2 customer service across phone, email, chat.",
        owner=user.email,
        criticality=Criticality.HIGH,
        rto_minutes=240,
        rpo_minutes=60,
    )
    db.add_all([payments, checkout, support])
    await db.flush()

    # BCP for Payments
    bcp = BCP(
        function_id=payments.id,
        title="Payments Continuity Plan — Regional Datacenter Outage",
        summary=(
            "Maintain card-processing capability during a regional datacenter "
            "outage at peak hours, ensuring zero revenue loss and full "
            "PCI-DSS compliance."
        ),
        status=BCPStatus.DRAFT,
        content={
            "objectives": [
                "Restore checkout to ≤15 min RTO with ≤5 min RPO.",
                "Maintain ≥95% of baseline payment conversion rate.",
                "Issue customer comms within 30 min of incident declaration.",
            ],
            "activation_triggers": [
                "Primary DB cluster unreachable >2 minutes",
                "Payment success rate drops below 95% baseline",
                "PagerDuty SEV-1 declared by Engineering on-call",
            ],
            "procedures": [
                {
                    "step": 1,
                    "action": "SOC declares incident, pages on-call DBA + VP E-commerce",
                    "owner": "SOC",
                    "duration_minutes": 2,
                },
                {
                    "step": 2,
                    "action": "Failover transaction DB to Region-B standby cluster",
                    "owner": "DBA",
                    "duration_minutes": 5,
                },
                {
                    "step": 3,
                    "action": "Update DNS to route checkout API to Region-B",
                    "owner": "Platform",
                    "duration_minutes": 3,
                },
                {
                    "step": 4,
                    "action": "Validate payment conversion vs baseline",
                    "owner": "Engineering",
                    "duration_minutes": 5,
                },
                {
                    "step": 5,
                    "action": "Publish customer-facing status update",
                    "owner": "Comms",
                    "duration_minutes": 5,
                },
            ],
            "recovery_targets": {"rto_minutes": 60, "rpo_minutes": 15},
        },
        gaps=[
            {
                "severity": "high",
                "area": "data_consistency",
                "issue": "No documented procedure for verifying cardholder data consistency post-failover",
                "recommendation": "Add automated reconciliation step between Region-A and Region-B",
            },
            {
                "severity": "medium",
                "area": "third_party",
                "issue": "Acquiring bank settlement API not listed as a dependency",
                "recommendation": "Add to dependencies and test their DR posture",
            },
        ],
    )
    db.add(bcp)

    impact = ImpactAssessment(
        function_id=payments.id,
        scenario="8-hour datacenter outage during Black Friday peak",
        description=(
            "Complete loss of card processing during Black Friday peak eliminates "
            "all online revenue, triggers card-network penalties, and drives "
            "customers to competitors. Social media erupts within 15 minutes."
        ),
        revenue_impact_usd=2_400_000,
        operational_impact_score=10,
        reputation_impact_score=9,
        details={
            "timeline": {
                "first_hour": "Queue grows; SLAs breach",
                "first_day": "Social-media backlash; press picks up the outage",
                "first_week": "Customer churn measurable in recurring orders",
            },
        },
    )
    db.add(impact)

    strategies = [
        RecoveryStrategy(
            function_id=payments.id,
            title="Active-active multi-region cloud cluster",
            kind=StrategyKind.REDUNDANCY,
            description="Real-time replication + automatic DNS/API failover. Meets RTO/RPO with margin.",
            estimated_cost_usd=240_000,
            rto_minutes=5,
            rpo_minutes=1,
            is_recommended=True,
            details={"rationale": "Best balance of cost and recovery; survives any single-region failure."},
        ),
        RecoveryStrategy(
            function_id=payments.id,
            title="Warm standby in secondary cloud region",
            kind=StrategyKind.WARM_SITE,
            description="Lower cost, manual failover. Tight under Black Friday load.",
            estimated_cost_usd=120_000,
            rto_minutes=30,
            rpo_minutes=5,
            is_recommended=False,
            details={"rationale": "Acceptable for non-peak windows."},
        ),
        RecoveryStrategy(
            function_id=payments.id,
            title="Cold DR with manual restore",
            kind=StrategyKind.COLD_SITE,
            description="Last-resort. Misses Black Friday targets by hours.",
            estimated_cost_usd=25_000,
            rto_minutes=480,
            rpo_minutes=1440,
            is_recommended=False,
            details={"rationale": "Useful only for non-critical paths."},
        ),
    ]
    db.add_all(strategies)
    await db.flush()

    exercise = Exercise(
        bcp_id=bcp.id,
        name="Black-Friday Ransomware Checkout Drill",
        scenario=(
            "Tuesday 09:42, 72h before Black-Friday launch. Anomalous encrypted "
            "file extensions detected on the primary transaction DB cluster; "
            "checkout API begins returning 503 within four minutes."
        ),
        objectives=[
            "Failover under 30 minutes",
            "Customer comms in <10 minutes",
            "PCI containment workflow within 1 hour",
        ],
        status=ExerciseStatus.COMPLETED,
        score=68,
        evaluation={
            "strengths": [
                "PCI forensic containment workflow executed within 1-hour target",
                "Customer communications issued at T+8 minutes, beating 30-minute SLA",
            ],
            "weaknesses": [
                "RTO missed: 22 min vs ≤15 min target",
                "RPO missed: 45 min vs ≤5 min target due to stale snapshot",
            ],
            "recommendations": [
                "Reduce backup interval to ≤5 min (continuous replication)",
                "Automate Region-B failover playbook to cut RTO to ≤15 min",
            ],
        },
        started_at=datetime(2026, 4, 15, 9, 42, tzinfo=UTC),
        completed_at=datetime(2026, 4, 15, 11, 5, tzinfo=UTC),
    )
    db.add(exercise)
    await db.flush()

    return [payments.id, checkout.id, support.id]


async def _seed_vendors(db: AsyncSession) -> list[uuid.UUID]:
    stripe = Vendor(
        name=f"Stripe Inc [{secrets.token_hex(3)}]",
        description="Payment processor — handles all US card transactions.",
        contact="vendor-mgmt@demo.dclaw.app",
        services_provided="card processing, fraud detection",
        tier="tier-1",
        readiness_score=85,
    )
    db.add(stripe)
    await db.flush()

    assessment = VendorAssessment(
        vendor_id=stripe.id,
        readiness_score=85,
        risk_level="medium",
        summary=(
            "Stripe demonstrates mature continuity practices with redundant "
            "global infrastructure and a strong compliance posture, but "
            "single-vendor dependency for 100% of US card volume creates "
            "systemic risk."
        ),
        details={
            "strengths": ["Redundant DCs across 3 regions", "Documented DR plan"],
            "weaknesses": ["Single-vendor dependency", "No documented manual fallback"],
            "monitoring_indicators": [
                "Stripe status page incident frequency >2 per quarter",
                "API error rate spikes >0.1% for 5+ minutes",
                "Settlement delays >24 hours",
            ],
        },
    )
    db.add(assessment)
    await db.flush()

    return [stripe.id]
