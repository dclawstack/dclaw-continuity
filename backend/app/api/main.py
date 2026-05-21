from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import health
from app.api.v1 import (
    attachments,
    auth,
    bcps,
    communications,
    copilot,
    crisis,
    demo,
    dependencies,
    exercises,
    functions,
    impact,
    it_dr,
    recovery,
    regulatory,
    supply_chain,
    vendors,
    work_area,
)
from app.core.config import settings
from app.core.database import init_db
from app.core.logging import configure_logging

configure_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.2.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(demo.router, prefix="/api/v1/demo", tags=["demo"])

# Prometheus /metrics — Counter/Histogram per endpoint + status code.
# Excludes /health and /metrics itself from the request-counter to keep
# the series cardinality low.
Instrumentator(
    excluded_handlers=["/health/.*", "/metrics"],
    should_group_status_codes=True,
    should_ignore_untemplated=True,
).instrument(app).expose(
    app,
    endpoint="/metrics",
    include_in_schema=False,
    tags=["monitoring"],
)

# P0
app.include_router(functions.router, prefix="/api/v1/functions", tags=["functions"])
app.include_router(bcps.router, prefix="/api/v1/bcps", tags=["bcps"])
app.include_router(attachments.router, prefix="/api/v1/bcps", tags=["bcp-attachments"])
app.include_router(impact.router, prefix="/api/v1/impact", tags=["impact"])
app.include_router(recovery.router, prefix="/api/v1/recovery", tags=["recovery"])
app.include_router(dependencies.router, prefix="/api/v1/dependencies", tags=["dependencies"])
app.include_router(copilot.router, prefix="/api/v1/copilot", tags=["copilot"])

# P1
app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["exercises"])
app.include_router(crisis.router, prefix="/api/v1/crisis", tags=["crisis"])
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["vendors"])
app.include_router(communications.router, prefix="/api/v1/communications", tags=["communications"])

# P2
app.include_router(work_area.router, prefix="/api/v1/work-area", tags=["work-area"])
app.include_router(it_dr.router, prefix="/api/v1/it-dr", tags=["it-dr"])
app.include_router(supply_chain.router, prefix="/api/v1/supply-chain", tags=["supply-chain"])
app.include_router(regulatory.router, prefix="/api/v1/regulatory", tags=["regulatory"])
