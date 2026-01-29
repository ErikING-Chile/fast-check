from __future__ import annotations

from typing import List

from core.models import Segment, Transcript


def apply_edits(transcript: Transcript, edits: List[dict]) -> Transcript:
    segments = [segment.model_copy() for segment in transcript.segments]
    for edit in edits:
        action = edit.get("action")
        if action == "rename":
            old = edit.get("old")
            new = edit.get("new")
            for segment in segments:
                if segment.speaker == old:
                    segment.speaker = new
        elif action == "assign":
            start = edit.get("start")
            end = edit.get("end")
            speaker = edit.get("speaker")
            for segment in segments:
                if segment.start >= start and segment.end <= end:
                    segment.speaker = speaker
        elif action == "split":
            time = edit.get("time")
            speaker = edit.get("speaker")
            updated: List[Segment] = []
            for segment in segments:
                if segment.start < time < segment.end:
                    updated.append(
                        Segment(
                            start=segment.start,
                            end=time,
                            speaker=segment.speaker,
                            text=segment.text,
                        )
                    )
                    updated.append(
                        Segment(
                            start=time,
                            end=segment.end,
                            speaker=speaker or segment.speaker,
                            text=segment.text,
                        )
                    )
                else:
                    updated.append(segment)
            segments = updated
        elif action == "merge":
            start = edit.get("start")
            end = edit.get("end")
            merged: List[Segment] = []
            buffer: List[Segment] = []
            for segment in segments:
                if segment.start >= start and segment.end <= end:
                    buffer.append(segment)
                else:
                    if buffer:
                        merged.append(_merge_buffer(buffer))
                        buffer = []
                    merged.append(segment)
            if buffer:
                merged.append(_merge_buffer(buffer))
            segments = merged
    return Transcript(segments=segments)


def _merge_buffer(buffer: List[Segment]) -> Segment:
    speaker = buffer[0].speaker
    text = " ".join(segment.text for segment in buffer)
    return Segment(
        start=buffer[0].start,
        end=buffer[-1].end,
        speaker=speaker,
        text=text,
    )
