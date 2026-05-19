"""P1/P2 feature stubs.

These endpoints return 501 until the corresponding feature is implemented in
subsequent PRs. They exist so the API surface matches REVISED-PRD.md and
consumers can discover them.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status


def _stub(feature: str):
    async def handler():
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{feature} not yet implemented (see REVISED-PRD.md)",
        )

    return handler


# P1
exercises_router = APIRouter()
exercises_router.add_api_route("/", _stub("P1.1 Exercise Management"), methods=["GET"])

crisis_router = APIRouter()
crisis_router.add_api_route("/", _stub("P1.2 Crisis Integration"), methods=["GET"])

vendors_router = APIRouter()
vendors_router.add_api_route("/", _stub("P1.3 Vendor Continuity"), methods=["GET"])

communications_router = APIRouter()
communications_router.add_api_route(
    "/", _stub("P1.4 Communication Plans"), methods=["GET"]
)


# P2
work_area_router = APIRouter()
work_area_router.add_api_route("/", _stub("P2.1 Work Area Recovery"), methods=["GET"])

it_dr_router = APIRouter()
it_dr_router.add_api_route("/", _stub("P2.2 IT DR Planning"), methods=["GET"])

supply_chain_router = APIRouter()
supply_chain_router.add_api_route(
    "/", _stub("P2.3 Supply Chain Continuity"), methods=["GET"]
)

regulatory_router = APIRouter()
regulatory_router.add_api_route(
    "/", _stub("P2.4 Regulatory Reporting"), methods=["GET"]
)
