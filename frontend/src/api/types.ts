export type Role = "user" | "assistant";

export interface MessageContext {
  message_id: string;
  interaction_id: string;
  thread_id: string;
  role: Role;
}

export interface MessageBody {
  text: string;
  entities: string[];
}

export interface MessageResponse {
  context: MessageContext;
  body: MessageBody;
}

export interface ThreadResponse {
  thread_id: string;
}

export interface ThreadSummary {
  thread_id: string;
  title: string | null;
}

export interface ThreadListResponse {
  threads: ThreadSummary[];
  has_more: boolean;
}

export interface ThreadMessagesResponse {
  thread_id: string;
  messages: MessageResponse[];
}

export interface InteractionResponse {
  thread_id: string;
  interaction_id: string;
  user_message: MessageResponse;
  assistant_message: MessageResponse | null;
}

export interface ChatRequest {
  type: "message";
  thread_id: string | null;
  message: string;
}

export interface TraceEvent {
  interaction_id: string;
  node: string; // e.g. "understand", "api_call"
  status: "started" | "completed" | "failed";
  data: Record<string, unknown>;
}

export type ChatEvent =
  | { type: "trace"; data: TraceEvent }
  | { type: "interaction_completed"; data: InteractionResponse }
  | { type: "error"; message: string; details?: unknown };
