from __future__ import annotations

from pathlib import Path

from utils.ffmpeg import run_ffmpeg


def extract_audio(video_path: Path, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-ac",
        "1",
        "-ar",
        "16000",
        str(output_path),
    ]
    run_ffmpeg(command)
