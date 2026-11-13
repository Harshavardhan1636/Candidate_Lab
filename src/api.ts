export type User = {
  id: string;
  email: string;
  role: "recruiter" | "candidate" | "auditor";
};
export type Job = {
  id: string;
  title: string;
  description: string;
  required: string[];
  preferred: string[];
  version: number;
  created: string;
};
export type Candidate = {
  id: string;
  label: string;
  text?: string;
  skills: {
    skill: string;
    passage: string;
    status?: string;
    notes?: string[];
  }[];
  warnings: string[];
  version: number;
  synthetic: boolean;
  updated: string;
};
export type Result = {
  candidate_id: string;
  candidate_label: string;
  profile_version: number;
  score: number;
  components: {
    name: string;
    value: number;
    weight: number;
    contribution: number;
  }[];
  requirements: {
    skill: string;
    kind: string;
    matched: boolean;
    evidence: string | null;
    evidence_status?: string;
    notes?: string[];
  }[];
  warnings: string[];
  review?: { status: string; reason: string; created: string };
  status: string;
};
export type Run = {
  id: string;
  job_id: string;
  job_snapshot: Job & { scope?: string; application_ids?: string[] };
  method: string;
  candidate_count: number;
  created: string;
  results?: Result[];
};
export type Audit = {
  run_id: string;
  threshold: number;
  job_title: string;
  method: string;
  audited_count: number;
  unattributed_count: number;
  demographic_parity_difference: number | null;
  provenance: string;
  limitations: string[];
  groups: {
    group: string;
    count: number;
    selected: number | null;
    selection_rate: number | null;
    interval: number[] | null;
    suppressed: boolean;
  }[];
};
export type Page<T> = { items: T[]; total: number };
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
  ) {
    super(message);
  }
}
export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers =
    init.body instanceof FormData
      ? init.headers
      : { "Content-Type": "application/json", ...init.headers };
  const response = await fetch(`/api${path}`, {
    ...init,
    headers,
    credentials: "include",
  });
  if (!response.ok) {
    if (
      response.status === 401 &&
      path !== "/auth/login" &&
      path !== "/auth/me"
    ) {
      window.dispatchEvent(new Event("session-expired"));
    }
    const body = await response
      .json()
      .catch(() => ({ detail: "The server returned an unreadable response." }));
    const detail = Array.isArray(body.detail)
      ? body.detail.map((x: { msg: string }) => x.msg).join(" ")
      : body.detail;
    throw new ApiError(
      detail || `Request failed (${response.status}).`,
      response.status,
    );
  }
  return response.json();
}
export function date(value: string) {
  return new Intl.DateTimeFormat("en-IN", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}
export function method(value: string) {
  return value.includes("semantic")
    ? "Local semantic model"
    : "TF-IDF + skill evidence";
}
