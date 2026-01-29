import type { JobResult } from "../types/models";

const API_BASE = "http://localhost:8000";

export async function createJob(payload: {
  video_path: string;
  language: string;
  num_speakers?: number | null;
  pack_name?: string | null;
  verify: boolean;
}): Promise<{ job_id: string }> {
  const response = await fetch(`${API_BASE}/api/jobs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) {
    throw new Error("Failed to create job");
  }
  return response.json();
}

export async function getJobStatus(jobId: string): Promise<{
  status: string;
  progress: number;
  current_step: string;
  logs: string[];
}> {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}`);
  if (!response.ok) {
    throw new Error("Failed to fetch job status");
  }
  return response.json();
}

export async function getResult(jobId: string): Promise<JobResult> {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}/result?apply_edits=true`);
  if (!response.ok) {
    throw new Error("Failed to fetch result");
  }
  return response.json();
}

export async function saveEdits(jobId: string, edits: Array<Record<string, unknown>>) {
  const response = await fetch(`${API_BASE}/api/jobs/${jobId}/edits`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ edits }),
  });
  if (!response.ok) {
    throw new Error("Failed to save edits");
  }
  return response.json();
}

export async function pickFile(): Promise<{ path: string }> {
  const response = await fetch(`${API_BASE}/api/utils/pick-file`);
  if (!response.ok) {
    throw new Error("Failed to pick file");
  }
  return response.json();
}
