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
