from __future__ import annotations

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

# Numpy 2.x backward compatibility hack
import numpy as np
try:
    if not hasattr(np, "NaN"):
        np.NaN = np.nan
    if not hasattr(np, "float_"):
        np.float_ = np.float64
    if not hasattr(np, "Infinity"):
        np.Infinity = np.inf
    if not hasattr(np, "complex_"):
        np.complex_ = np.complex128
except Exception:
    pass

# Auto-patch dependencies for compatibility
try:
    from patch_dependencies import patch_dependencies
    patch_dependencies()
except ImportError:
    pass
except Exception as e:
    print(f"Warning: Failed to patch dependencies: {e}")

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
