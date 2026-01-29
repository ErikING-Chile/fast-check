from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import List

from core.models import Segment
from utils.ffmpeg import get_audio_duration


def transcribe_audio(audio_path: Path, language: str) -> List[Segment]:
    if importlib.util.find_spec("faster_whisper") is not None:
        from faster_whisper import WhisperModel  # type: ignore

        model = WhisperModel("small", device="cpu", compute_type="int8")
        segments, _ = model.transcribe(str(audio_path), language=language if language != "auto" else None)
        return [
            Segment(
                start=float(segment.start),
                end=float(segment.end),
                speaker="",
                text=segment.text.strip(),
            )
            for segment in segments
        ]
    if importlib.util.find_spec("whisper") is not None:
        import whisper  # type: ignore

        model = whisper.load_model("small")
        result = model.transcribe(str(audio_path), language=None if language == "auto" else language)
        return [
            Segment(
                start=float(segment["start"]),
                end=float(segment["end"]),
                speaker="",
                text=segment["text"].strip(),
            )
            for segment in result.get("segments", [])
        ]

    duration = get_audio_duration(audio_path)
    return [
        Segment(
            start=0.0,
            end=duration,
            speaker="",
            text="[transcription unavailable - install faster-whisper]",
        )
    ]
