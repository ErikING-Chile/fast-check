from __future__ import annotations

from typing import List

from core.models import Segment


def _overlap(a_start: float, a_end: float, b_start: float, b_end: float) -> float:
    return max(0.0, min(a_end, b_end) - max(a_start, b_start))


def merge_segments(diarized: List[Segment], transcribed: List[Segment]) -> List[Segment]:
    if not diarized:
        return [
            Segment(
                start=segment.start,
                end=segment.end,
                speaker="SPEAKER_00",
                text=segment.text,
            )
            for segment in transcribed
        ]

    merged: List[Segment] = []
    for segment in transcribed:
        best_speaker = diarized[0].speaker
        best_overlap = 0.0
        for diarized_segment in diarized:
            overlap = _overlap(
                segment.start, segment.end, diarized_segment.start, diarized_segment.end
            )
            if overlap > best_overlap:
                best_overlap = overlap
                best_speaker = diarized_segment.speaker
        merged.append(
            Segment(
                start=segment.start,
                end=segment.end,
                speaker=best_speaker,
                text=segment.text,
            )
        )
    return merged
