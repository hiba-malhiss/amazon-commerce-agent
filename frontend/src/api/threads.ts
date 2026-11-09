import { THREADS_PAGE_SIZE } from "../config";
import type { ThreadListResponse, ThreadMessagesResponse, ThreadResponse } from "./types";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, init);
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}${detail ? `: ${detail}` : ""}`);
  }
  return res.json() as Promise<T>;
}

export function createThread(): Promise<ThreadResponse> {
  return request<ThreadResponse>("/threads", { method: "POST" });
}

export function listThreads(offset = 0): Promise<ThreadListResponse> {
  const query = new URLSearchParams({ limit: String(THREADS_PAGE_SIZE), offset: String(offset) });
  return request<ThreadListResponse>(`/threads?${query}`);
}

export function getThreadMessages(threadId: string): Promise<ThreadMessagesResponse> {
  return request<ThreadMessagesResponse>(`/threads/${threadId}/messages`);
}
