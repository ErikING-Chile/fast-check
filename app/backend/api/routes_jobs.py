from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from core.models import JobResult
from core.settings import SETTINGS
from pipeline.job_manager import JOB_MANAGER
from pipeline.steps.edits import apply_edits
from utils.time import seconds_to_timestamp, seconds_to_vtt

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("")
async def create_job(body: dict) -> dict:
    try:
        job_id = JOB_MANAGER.submit(
            video_path=body["video_path"],
            language=body.get("language", "auto"),
            num_speakers=body.get("num_speakers"),
            pack_name=body.get("pack_name"),
            verify=bool(body.get("verify", False)),
        )
        return {"job_id": job_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{job_id}")
async def get_job(job_id: str) -> dict:
    status = JOB_MANAGER.get_status(job_id)
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "status": status.status,
        "progress": status.progress,
        "current_step": status.current_step,
        "logs": status.logs,
    }


@router.get("/{job_id}/result")
async def get_result(job_id: str, apply_edits: bool = True) -> JSONResponse:
    result = JOB_MANAGER.get_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    if apply_edits:
        edits_path = SETTINGS.data_dir / "jobs" / job_id / "edits.json"
        if edits_path.exists():
            edits = json.loads(edits_path.read_text())
            result = _apply_edits(result, edits)
    return JSONResponse(result.model_dump())


@router.patch("/{job_id}/edits")
async def update_edits(job_id: str, body: dict) -> dict:
    edits_path = SETTINGS.data_dir / "jobs" / job_id / "edits.json"
    edits_path.parent.mkdir(parents=True, exist_ok=True)
    edits_path.write_text(json.dumps(body.get("edits", []), indent=2))
    return {"status": "saved"}


@router.get("/{job_id}/export/{format}")
async def export_result(job_id: str, format: str) -> FileResponse:
    result = JOB_MANAGER.get_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    export_dir = SETTINGS.data_dir / "jobs" / job_id / "exports"
    export_dir.mkdir(parents=True, exist_ok=True)
    if format == "json":
        path = export_dir / "result.json"
        path.write_text(result.model_dump_json(indent=2))
    elif format == "csv":
        path = export_dir / "claims.csv"
        _export_csv(path, result)
    elif format == "srt":
        path = export_dir / "transcript.srt"
        _export_srt(path, result)
    elif format == "vtt":
        path = export_dir / "transcript.vtt"
        _export_vtt(path, result)
    else:
        raise HTTPException(status_code=400, detail="Unsupported format")
    return FileResponse(path)


def _export_csv(path: Path, result: JobResult) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["claim_id", "speaker", "start", "end", "text"])
        for claim in result.claims:
            writer.writerow([claim.id, claim.speaker, claim.start, claim.end, claim.text])


def _export_srt(path: Path, result: JobResult) -> None:
    lines = []
    for idx, segment in enumerate(result.transcript.segments, start=1):
        lines.append(str(idx))
        lines.append(
            f"{seconds_to_timestamp(segment.start)} --> {seconds_to_timestamp(segment.end)}"
        )
        lines.append(f"{segment.speaker}: {segment.text}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _export_vtt(path: Path, result: JobResult) -> None:
    lines = ["WEBVTT", ""]
    for segment in result.transcript.segments:
        lines.append(
            f"{seconds_to_vtt(segment.start)} --> {seconds_to_vtt(segment.end)}"
        )
        lines.append(f"{segment.speaker}: {segment.text}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def _apply_edits(result: JobResult, edits: list[dict]) -> JobResult:
    transcript = apply_edits(result.transcript, edits)
    return JobResult(
        metadata=result.metadata,
        transcript=transcript,
        claims=result.claims,
        verifications=result.verifications,
    )
