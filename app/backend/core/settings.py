from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


@dataclass
class Settings:
    data_dir: Path = Path("app/data")
    packs_dir: Path = Path("app/packs")
    allowlist_domains: List[str] = field(default_factory=lambda: ["example.com"]) 
    default_language: str = "auto"
    default_num_speakers: Optional[int] = None
    asr_model: str = "small"
    use_vad: bool = True
    licensing_enabled: bool = False


SETTINGS = Settings()
