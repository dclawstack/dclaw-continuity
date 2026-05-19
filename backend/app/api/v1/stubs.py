"""P2 feature stubs.

These endpoints return 501 until the corresponding feature is implemented in
PR 4. They exist so the API surface matches REVISED-PRD.md.
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
