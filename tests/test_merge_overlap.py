from core.models import Segment
from pipeline.steps.merge import merge_segments


def test_merge_overlap_assigns_best_speaker():
    diarized = [
        Segment(start=0.0, end=5.0, speaker="A", text=""),
        Segment(start=5.0, end=10.0, speaker="B", text=""),
    ]
    transcribed = [
        Segment(start=1.0, end=4.0, speaker="", text="hola"),
        Segment(start=6.0, end=9.0, speaker="", text="adios"),
    ]
    merged = merge_segments(diarized, transcribed)
    assert merged[0].speaker == "A"
    assert merged[1].speaker == "B"
