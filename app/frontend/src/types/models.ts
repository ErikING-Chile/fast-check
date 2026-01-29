export interface Segment {
  start: number;
  end: number;
  speaker: string;
  text: string;
}

export interface Transcript {
  segments: Segment[];
}

export interface Claim {
  id: string;
  speaker: string;
  start: number;
  end: number;
  text: string;
  type: string;
  confidence: number;
}

export interface Citation {
  source_title: string;
  source_ref: string;
  snapshot_date?: string;
  page?: number;
  excerpt: string;
}

export interface Verification {
  claim_id: string;
  status: string;
  confidence: number;
  citations: Citation[];
}

export interface JobResult {
  metadata: {
    job_id: string;
    video_path: string;
    language: string;
    num_speakers?: number | null;
    pack_name?: string | null;
    verify: boolean;
  };
  transcript: Transcript;
  claims: Claim[];
  verifications: Verification[];
}
