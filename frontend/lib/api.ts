export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

export type JobStatus =
  | "UPLOADED"
  | "PARSING"
  | "ALIGNING"
  | "REWRITING"
  | "VALIDATING"
  | "BUILDING"
  | "COMPLETED"
  | "FAILED"
  | "MANUAL_REVIEW";

export type Job = {
  job_id: string;
  status: JobStatus;
  progress: number;
  created_at: string;
  updated_at: string;
  output_docx_path?: string | null;
  change_report_path?: string | null;
  error_message?: string | null;
  timeline: string[];
  total_units: number;
  rewritten_units: number;
  manual_review_units: number;
  provider_fail_count: number;
};

export type RepairUnit = {
  id: string;
  paragraph_ref: string;
  risk_type: string;
  similarity_score: number;
  original_text: string;
  report_excerpt?: string | null;
  provider_used?: string | null;
  rewritten_text?: string | null;
  summary_of_changes?: string | null;
  citation_needed?: boolean | null;
  confidence?: number | null;
  status: string;
  failure_reason?: string | null;
};

export async function createJob(formData: FormData) {
  const response = await fetch(`${API_BASE_URL}/jobs`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) {
    throw new Error(await response.text());
  }
  return response.json();
}

export async function getJob(jobId: string): Promise<Job> {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Khong the tai thong tin job");
  }
  return response.json();
}

export async function getUnits(jobId: string): Promise<RepairUnit[]> {
  const response = await fetch(`${API_BASE_URL}/jobs/${jobId}/units`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Khong the tai danh sach unit");
  }
  return response.json();
}
