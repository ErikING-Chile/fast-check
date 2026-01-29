from __future__ import annotations

import json
import subprocess
from pathlib import Path


def run_ffmpeg(command: list[str]) -> None:
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    if process.returncode != 0:
        raise RuntimeError(process.stderr.strip() or "ffmpeg failed")


def get_audio_duration(audio_path: Path) -> float:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "json",
        str(audio_path),
    ]
    process = subprocess.run(command, capture_output=True, text=True, check=False)
    if process.returncode != 0:
        return 0.0
    data = json.loads(process.stdout)
    return float(data.get("format", {}).get("duration", 0.0))
