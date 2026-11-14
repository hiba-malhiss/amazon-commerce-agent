export type Role = "user" | "assistant";

export interface MessageContext {
  message_id: string;
  interaction_id: string;
  thread_id: string;
  role: Role;
}

// One result shown under an assistant reply; "the second one" means number 2
export interface Card {
  number: number;
  reference: string;
  entity_code: string; // e.g. "product"
  label: string; // its name
  attributes: Record<string, unknown>;
}

export interface MessageBody {
  text: string;
  entities: Card[]; // the reply's cards, number 1 first
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

export interface PromptEvent {
  interaction_id: string;
  node: string; // "understand" or "respond"
  prompt: string; // every message sent to the LLM, each labelled by role
}

export type ChatEvent =
  | { type: "trace"; data: TraceEvent }
  | { type: "prompt"; data: PromptEvent }
  | { type: "interaction_completed"; data: InteractionResponse }
  | { type: "error"; message: string; details?: unknown };
