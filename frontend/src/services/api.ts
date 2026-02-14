const API_BASE = import.meta.env.VITE_API_BASE_URL || "https://starstruck-backend-production.up.railway.app";

export async function connectService(service: string, username: string): Promise<{ success: boolean; preview: string }> {
  const res = await fetch(`${API_BASE}/api/connect`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ service, username }),
  });
  return res.json();
}

export interface AnalysisResult {
  bio: string;
  findings: { label: string; value: string; detail: string }[];
  tags: string[];
  schedule: string;
  dossier: Record<string, unknown>;
}

export async function analyzeUser(identifiers: Record<string, string | null>): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ identifiers }),
  });
  return res.json();
}

export interface UserInput {
  spotify_username?: string;
  letterboxd_username?: string;
  github_username?: string;
  book_titles?: string[];
  location?: string;
}

export interface MatchRequest {
  user_a: UserInput;
  user_b: UserInput;
  include_venue: boolean;
}

export interface CoachingResponse {
  venues: any[];
  coaching_a: any;
  coaching_b: any;
  cross_ref: any;
}

export async function runPipeline(request: MatchRequest): Promise<CoachingResponse> {
  const res = await fetch(`${API_BASE}/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });
  if (!res.ok) throw new Error("Failed to run pipeline");
  return res.json();
}
