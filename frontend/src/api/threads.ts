import { THREADS_PAGE_SIZE } from "../config";
import { request } from "./http";
import type { PromptEvent, ThreadListResponse, ThreadMessagesResponse, ThreadResponse, TraceEvent } from "./types";

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

export interface InteractionTrace {
  events: TraceEvent[];
  prompts: PromptEvent[];
}

export function getInteractionTrace(interactionId: string): Promise<InteractionTrace> {
  return request<InteractionTrace>(`/interactions/${interactionId}/events`);
}
