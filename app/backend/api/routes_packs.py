from __future__ import annotations

from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import requests
from fastapi import APIRouter, HTTPException

from core.settings import SETTINGS
from indexing.vectorstore import VectorStore

router = APIRouter(prefix="/api/packs", tags=["packs"])


@router.post("/index")
async def index_pack(body: dict) -> dict:
    pack_name = body["pack_name"]
    store = VectorStore.from_pack(pack_name)
    store.build()
    return {"status": "indexed", "pack": pack_name}


@router.post("/snapshot")
async def snapshot_pack(body: dict) -> dict:
    pack_name = body["pack_name"]
    url = body["url"]
    parsed = urlparse(url)
    if parsed.hostname not in SETTINGS.allowlist_domains:
        raise HTTPException(status_code=403, detail="Domain not allowlisted")
    response = requests.get(url, timeout=20)
    response.raise_for_status()
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    snapshot_dir = SETTINGS.data_dir / "snapshots" / parsed.hostname / timestamp
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    filename = Path(parsed.path).name or "index.html"
    snapshot_path = snapshot_dir / filename
    snapshot_path.write_text(response.text, encoding="utf-8")

    pack_dir = SETTINGS.packs_dir / pack_name
    pack_dir.mkdir(parents=True, exist_ok=True)
    target_path = pack_dir / f"snapshot_{parsed.hostname}_{timestamp}.html"
    target_path.write_text(response.text, encoding="utf-8")
    return {"status": "saved", "path": str(target_path)}
