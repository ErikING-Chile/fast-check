from __future__ import annotations

import asyncio
import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from core.engine import run_pipeline
from core.models import JobResult
from core.settings import SETTINGS


@dataclass
class JobStatus:
    job_id: str
    status: str = "queued"
    progress: float = 0.0
    current_step: str = "queued"
    logs: list[str] = field(default_factory=list)
    result_path: Optional[Path] = None


class JobManager:
    def __init__(self) -> None:
        self._queue: asyncio.Queue[dict] = asyncio.Queue()
        self._jobs: Dict[str, JobStatus] = {}
        self._worker_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        if self._worker_task is None:
            self._worker_task = asyncio.create_task(self._worker())

    def submit(
        self,
        video_path: str,
        language: str,
        num_speakers: Optional[int],
        pack_name: Optional[str],
        verify: bool,
    ) -> str:
        if not Path(video_path).exists():
            raise ValueError(f"Video file not found: {video_path}")
        if Path(video_path).stat().st_size == 0:
            raise ValueError(f"Video file is empty (0 bytes): {video_path}")

        job_id = str(uuid.uuid4())
        status = JobStatus(job_id=job_id)
        self._jobs[job_id] = status
        self._queue.put_nowait(
            {
                "job_id": job_id,
                "video_path": video_path,
                "language": language,
                "num_speakers": num_speakers,
                "pack_name": pack_name,
                "verify": verify,
            }
        )
        return job_id

    def get_status(self, job_id: str) -> Optional[JobStatus]:
        return self._jobs.get(job_id)

    def get_result(self, job_id: str) -> Optional[JobResult]:
        status = self._jobs.get(job_id)
        if not status or not status.result_path or not status.result_path.exists():
            return None
        data = json.loads(status.result_path.read_text())
        return JobResult.model_validate(data)

    async def _worker(self) -> None:
        while True:
            job = await self._queue.get()
            job_id = job["job_id"]
            status = self._jobs[job_id]
            status.status = "running"
            status.current_step = "pipeline"
            status.progress = 0.1
            status.logs.append("Starting pipeline")
            try:
                result = run_pipeline(**job)
                status.progress = 0.9
                status.current_step = "saving"
                result_path = SETTINGS.data_dir / "jobs" / job_id / "result.json"
                result_path.write_text(result.model_dump_json(indent=2))
                status.result_path = result_path
                status.progress = 1.0
                status.status = "completed"
                status.current_step = "done"
                status.logs.append("Completed pipeline")
            except Exception as exc:  # noqa: BLE001 - job failure
                status.status = "failed"
                status.current_step = "error"
                status.logs.append(f"Error: {exc}")
            finally:
                self._queue.task_done()


JOB_MANAGER = JobManager()
