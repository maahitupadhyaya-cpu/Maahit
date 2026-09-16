import { SolveResponse } from "./types";

export class ApiRequestError extends Error {}

export async function solveProblem(category: string, problem: string): Promise<SolveResponse> {
  const res = await fetch("/api/solve", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ category, problem }),
  });
  if (!res.ok) {
    let detail = `Request failed with status ${res.status}`;
    try {
      const data = await res.json();
      if (data?.detail) detail = data.detail;
    } catch {
      // ignore
    }
    throw new ApiRequestError(detail);
  }
  return res.json();
}
