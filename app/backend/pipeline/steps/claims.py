from __future__ import annotations

import re
import uuid
from typing import List

from core.models import Claim, Transcript

CLAIM_PATTERN = re.compile(r"\b(\d+|porcentaje|millones|miles|es|son|fue|eran|será)\b", re.IGNORECASE)


def extract_claims(transcript: Transcript) -> List[Claim]:
    claims: List[Claim] = []
    for segment in transcript.segments:
        if CLAIM_PATTERN.search(segment.text):
            claims.append(
                Claim(
                    id=str(uuid.uuid4()),
                    speaker=segment.speaker,
                    start=segment.start,
                    end=segment.end,
                    text=segment.text,
                    type="statement",
                    confidence=0.55,
                )
            )
    return claims
