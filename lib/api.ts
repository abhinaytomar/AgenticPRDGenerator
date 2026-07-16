/** Typed fetch wrappers for each backend endpoint. */

import type {
  IntakeData,
  IntakeResponse,
  GenerateRequest,
  GenerateResponse,
  PRDDocument,
  TicketsResponse,
  FAQRequest,
  FAQResponse,
} from "./types";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

// Base URL for the API. In local dev, set NEXT_PUBLIC_API_BASE_URL to the
// FastAPI server (e.g. http://127.0.0.1:8000) so the browser calls it directly
// and skips Next's dev proxy (which drops long-running requests). In production
// leave it unset — calls go same-origin and Vercel routes /api to the function.
const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

async function post<T>(url: string, body: unknown, token?: string | null): Promise<T> {
  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${url}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const detail = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(detail.detail || `HTTP ${res.status}`, res.status);
  }

  return res.json() as Promise<T>;
}

export async function callIntake(intake: IntakeData, token?: string | null): Promise<IntakeResponse> {
  return post<IntakeResponse>("/api/intake", intake, token);
}

export async function callGenerate(req: GenerateRequest, token?: string | null): Promise<GenerateResponse> {
  return post<GenerateResponse>("/api/generate", req, token);
}

export async function callTickets(prd: PRDDocument, token?: string | null): Promise<TicketsResponse> {
  return post<TicketsResponse>("/api/tickets", { prd }, token);
}

export async function callFaq(req: FAQRequest, token?: string | null): Promise<FAQResponse> {
  return post<FAQResponse>("/api/faq", req, token);
}

export { ApiError };
