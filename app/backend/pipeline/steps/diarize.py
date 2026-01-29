from __future__ import annotations

import os
import importlib.util
from dotenv import load_dotenv

load_dotenv()
from pathlib import Path
from typing import List, Optional

from core.models import Segment
from utils.ffmpeg import get_audio_duration


def diarize_audio(audio_path: Path, num_speakers: Optional[int]) -> List[Segment]:
    duration = get_audio_duration(audio_path)
    if importlib.util.find_spec("pyannote.audio") is None:
        return [Segment(start=0.0, end=duration, speaker="SPEAKER_00", text="")]

    from pyannote.audio import Pipeline  # type: ignore

    # Try loading with explicit token (pyannote.audio 4.x uses 'token', older uses 'use_auth_token')
    token = os.environ.get("HF_TOKEN")
    auth_error = None

    try:
        # First try modern signature
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", token=token)
    except TypeError:
        # Fallback for older versions
        try:
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token=token)
        except Exception as e:
            auth_error = str(e)
            print(f"Error loading pyannote/speaker-diarization-3.1 (legacy auth): {e}")
            pipeline = None
    except Exception as e:
        auth_error = str(e)
        print(f"Error loading pyannote/speaker-diarization-3.1: {e}")
        pipeline = None

    if pipeline is None:
        # Fallback to older version or warn user
        try:
            pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization", use_auth_token=token)
        except Exception:
            pipeline = None
    
    if pipeline is None:
        error_msg = (
            f"Could not load pyannote pipeline. Error details: {auth_error}.\\n"
            "Please ensure you have accepted the user agreement at ALL of these pages:\\n"
            "1. https://huggingface.co/pyannote/speaker-diarization-3.1\\n"
            "2. https://huggingface.co/pyannote/segmentation-3.0\\n"
            "3. https://huggingface.co/pyannote/speaker-diarization-community-1 (NEW REQUIREMENT)\\n"
            "Check that your HF_TOKEN in .env is correct."
        )
        raise RuntimeError(error_msg)
    diarization = pipeline(str(audio_path))
    segments: List[Segment] = []
    for turn, _, speaker in diarization.itertracks(yield_label=True):
        segments.append(
            Segment(start=float(turn.start), end=float(turn.end), speaker=speaker, text="")
        )
    if num_speakers:
        segments = segments[:num_speakers]
    return segments
