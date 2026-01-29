from __future__ import annotations

from pathlib import Path
from typing import List, Optional

from core.models import Claim, JobMetadata, JobResult, Transcript
from core.settings import SETTINGS
from indexing.vectorstore import VectorStore
from pipeline.steps.claims import extract_claims
from pipeline.steps.diarize import diarize_audio
from pipeline.steps.extract_audio import extract_audio
from pipeline.steps.merge import merge_segments
from pipeline.steps.transcribe import transcribe_audio
from pipeline.steps.verify import verify_claims


def run_pipeline(
    job_id: str,
    video_path: str,
    language: str,
    num_speakers: Optional[int],
    pack_name: Optional[str],
    verify: bool,
) -> JobResult:
    data_dir = SETTINGS.data_dir / "jobs" / job_id
    data_dir.mkdir(parents=True, exist_ok=True)
    audio_path = data_dir / "audio.wav"

    extract_audio(Path(video_path), audio_path)
    diarized = diarize_audio(audio_path, num_speakers)
    transcribed = transcribe_audio(audio_path, language=language)
    merged = merge_segments(diarized, transcribed)
    transcript = Transcript(segments=merged)
    claims: List[Claim] = extract_claims(transcript)

    verifications = []
    if verify and pack_name:
        store = VectorStore.from_pack(pack_name)
        verifications = verify_claims(claims, store)

    metadata = JobMetadata(
        job_id=job_id,
        video_path=video_path,
        language=language,
        num_speakers=num_speakers,
        pack_name=pack_name,
        verify=verify,
    )
    return JobResult(
        metadata=metadata,
        transcript=transcript,
        claims=claims,
        verifications=verifications,
    )
