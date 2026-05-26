from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import CurrentUser, get_current_user
from app.core.database import get_db
from app.schemas.regulatory import (
    RegulatoryReportGenerateRequest,
    RegulatoryReportRead,
    RegulatoryReportSubmitRequest,
    RegulatoryReportUpdate,
)
from app.services import regulatory_service

router = APIRouter()


@router.get("", response_model=list[RegulatoryReportRead])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await regulatory_service.list_reports(db)


@router.post(
    "/generate",
    response_model=RegulatoryReportRead,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    payload: RegulatoryReportGenerateRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    return await regulatory_service.generate_report(db, payload)


@router.get("/{report_id}", response_model=RegulatoryReportRead)
async def get_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    r = await regulatory_service.get_report(db, report_id)
    if r is None:
        raise HTTPException(status_code=404, detail="report not found")
    return r


@router.patch("/{report_id}", response_model=RegulatoryReportRead)
async def update_report(
    report_id: uuid.UUID,
    payload: RegulatoryReportUpdate,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    r = await regulatory_service.get_report(db, report_id)
    if r is None:
        raise HTTPException(status_code=404, detail="report not found")
    return await regulatory_service.update_report(db, r, payload)


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    r = await regulatory_service.get_report(db, report_id)
    if r is None:
        raise HTTPException(status_code=404, detail="report not found")
    await regulatory_service.delete_report(db, r)


@router.post("/{report_id}/submit", response_model=RegulatoryReportRead)
async def submit_report(
    report_id: uuid.UUID,
    payload: RegulatoryReportSubmitRequest,
    db: AsyncSession = Depends(get_db),
    _: CurrentUser = Depends(get_current_user),
):
    r = await regulatory_service.get_report(db, report_id)
    if r is None:
        raise HTTPException(status_code=404, detail="report not found")
    return await regulatory_service.submit_report(db, r, payload)
