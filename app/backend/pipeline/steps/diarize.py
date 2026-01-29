from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import List, Optional

from core.models import Segment
from utils.ffmpeg import get_audio_duration


def diarize_audio(audio_path: Path, num_speakers: Optional[int]) -> List[Segment]:
    duration = get_audio_duration(audio_path)
    if importlib.util.find_spec("pyannote.audio") is None:
        return [Segment(start=0.0, end=duration, speaker="SPEAKER_00", text="")]

    from pyannote.audio import Pipeline  # type: ignore

    pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1")
    if pipeline is None:
        # Fallback to older version or warn user
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
    
    if pipeline is None:
        raise RuntimeError(
            "Could not load pyannote pipeline. Please ensure you have accepted the user agreement "
            "at https://huggingface.co/pyannote/speaker-diarization-3.1 and set your HF_TOKEN "
            "environment variable, or login using 'huggingface-cli login'."
        )
    diarization = pipeline(str(audio_path))
    segments: List[Segment] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append(
            Segment(start=float(turn.start), end=float(turn.end), speaker=speaker, text="")
        )
    if num_speakers:
        segments = segments[:num_speakers]
    return segments
