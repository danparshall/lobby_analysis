import type { Filing, Stats } from "./types";

// Relative URLs: proxied by Vite in dev, served by FastAPI in the build.
async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText} for ${path}`);
  }
  return res.json() as Promise<T>;
}

export function fetchStats(): Promise<Stats> {
  return getJSON<Stats>("/stats");
}

export function listFilings(params: {
  state?: string;
  filer_role?: string;
  limit?: number;
  offset?: number;
}): Promise<Filing[]> {
  const q = new URLSearchParams();
  if (params.state) q.set("state", params.state);
  if (params.filer_role) q.set("filer_role", params.filer_role);
  q.set("limit", String(params.limit ?? 50));
  q.set("offset", String(params.offset ?? 0));
  return getJSON<Filing[]>(`/filings?${q.toString()}`);
}

export function searchFilings(query: string, limit = 50): Promise<Filing[]> {
  const q = new URLSearchParams({ q: query, limit: String(limit) });
  return getJSON<Filing[]>(`/search?${q.toString()}`);
}

export function getFiling(id: string): Promise<Filing> {
  return getJSON<Filing>(`/filings/${encodeURIComponent(id)}`);
}
