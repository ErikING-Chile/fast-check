from __future__ import annotations

from fastapi import FastAPI

from api.routes_jobs import router as jobs_router
from api.routes_packs import router as packs_router
from pipeline.job_manager import JOB_MANAGER

app = FastAPI(title="FastCheck Local")

app.include_router(jobs_router)
app.include_router(packs_router)


@app.on_event("startup")
async def startup() -> None:
    JOB_MANAGER.start()
