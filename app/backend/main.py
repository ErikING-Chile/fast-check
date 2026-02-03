from __future__ import annotations

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

# Configurar torchaudio para evitar problemas con torchcodec en Windows
os.environ.setdefault("TORCHAUDIO_USE_BACKEND_DISPATCHER", "1")

# Numpy 2.x backward compatibility hack
import numpy as np
try:
    if not hasattr(np, "NaN"):
        np.NaN = np.nan
    if not hasattr(np, "NAN"):
        np.NAN = np.nan
    if not hasattr(np, "float_"):
        np.float_ = np.float64
    if not hasattr(np, "int_"):
        np.int_ = np.int64
    if not hasattr(np, "Infinity"):
        np.Infinity = np.inf
    if not hasattr(np, "Inf"):
        np.Inf = np.inf
    if not hasattr(np, "PINF"):
        np.PINF = np.inf
    if not hasattr(np, "NINF"):
        np.NINF = -np.inf
    if not hasattr(np, "PZERO"):
        np.PZERO = 0.0
    if not hasattr(np, "NZERO"):
        np.NZERO = -0.0
    if not hasattr(np, "complex_"):
        np.complex_ = np.complex128
    if not hasattr(np, "object_"):
        np.object_ = object
    if not hasattr(np, "str_"):
        np.str_ = np.str_
    if not hasattr(np, "bool8"):
        np.bool8 = np.bool_
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager para inicializar y limpiar recursos."""
    JOB_MANAGER.start()
    yield


app = FastAPI(title="FastCheck Local", lifespan=lifespan)

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
