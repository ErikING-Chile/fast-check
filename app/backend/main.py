from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes_jobs import router as jobs_router
from api.routes_packs import router as packs_router
from api.routes_utils import router as utils_router
from pipeline.job_manager import JOB_MANAGER

app = FastAPI(title="FastCheck Local")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router)
app.include_router(packs_router)
app.include_router(utils_router)


@app.on_event("startup")
async def startup() -> None:
    JOB_MANAGER.start()
