from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Segment(BaseModel):
    start: float
    end: float
    speaker: str
    text: str


class Transcript(BaseModel):
    segments: List[Segment]


class Claim(BaseModel):
    id: str
    speaker: str
    start: float
    end: float
    text: str
    type: str = "statement"
    confidence: float = 0.5
    context_before: Optional[str] = None
    context_after: Optional[str] = None


class Citation(BaseModel):
    source_title: str
    source_ref: str
    snapshot_date: Optional[str] = None
    page: Optional[int] = None
    excerpt: str


class Verification(BaseModel):
    claim_id: str
    status: str
    confidence: float
    citations: List[Citation] = Field(default_factory=list)


class JobMetadata(BaseModel):
    job_id: str
    video_path: str
    language: str
    num_speakers: Optional[int]
    pack_name: Optional[str] = None
    verify: bool = False


class JobResult(BaseModel):
    metadata: JobMetadata
    transcript: Transcript
    claims: List[Claim] = Field(default_factory=list)
    verifications: List[Verification] = Field(default_factory=list)
