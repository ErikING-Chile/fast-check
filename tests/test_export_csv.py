from pathlib import Path

from core.models import Claim, JobMetadata, JobResult, Transcript
from api.routes_jobs import _export_csv


def test_export_csv(tmp_path: Path):
    result = JobResult(
        metadata=JobMetadata(
            job_id="1",
            video_path="/tmp/video.mp4",
            language="es",
            num_speakers=2,
        ),
        transcript=Transcript(segments=[]),
        claims=[
            Claim(
                id="c1",
                speaker="S1",
                start=0.0,
                end=1.0,
                text="Hay 3 millones",
                type="statement",
                confidence=0.5,
            )
        ],
    )
    path = tmp_path / "claims.csv"
    _export_csv(path, result)
    content = path.read_text()
    assert "claim_id" in content
    assert "Hay 3 millones" in content
