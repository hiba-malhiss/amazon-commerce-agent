import type { TraceEvent } from "../../../api/types";

// The events of one message, regrouped in reasoning order:
// understanding → each request and its steps → response
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type EventData = Record<string, any>;

export type StepState = "running" | "completed" | "failed";

export interface Step {
  node: string;
  state: StepState;
  data: EventData; // the started event's data, then the completed / failed one's on top
}

export interface RequestTrace {
  id: string;
  resolution?: EventData; // the resolved request, or its clarification question
  steps: Step[]; // params_check, api_call / rag_search / missing_info
  workflow?: Step; // the tool workflow around the steps: its outcome or crash
}

export interface Reasoning {
  understand?: Step;
  resolve?: Step;
  requests: RequestTrace[];
  collect?: Step;
  respond?: Step;
}

const STAGES = ["understand", "resolve", "collect", "respond"] as const;
const STAGE_BY_NODE: Record<string, (typeof STAGES)[number]> = {
  understand: "understand",
  request_resolver: "resolve",
  collect: "collect",
  respond: "respond",
};

function toState(status: TraceEvent["status"]): StepState {
  return status === "started" ? "running" : status;
}

function merge(step: Step | undefined, event: TraceEvent): Step {
  return { node: event.node, state: toState(event.status), data: { ...step?.data, ...event.data } };
}

export function buildReasoning(events: TraceEvent[]): Reasoning {
  const reasoning: Reasoning = { requests: [] };

  const requestById = (id: string): RequestTrace => {
    let request = reasoning.requests.find((r) => r.id === id);
    if (!request) {
      request = { id, steps: [] };
      reasoning.requests.push(request);
    }
    return request;
  };

  for (const event of events) {
    const stage = STAGE_BY_NODE[event.node];
    if (stage) {
      reasoning[stage] = merge(reasoning[stage], event);
      // The resolver lists every request of the message, in order
      if (stage === "resolve" && event.status === "completed") {
        for (const resolved of (event.data.requests ?? []) as EventData[]) {
          requestById(resolved.id).resolution = resolved;
        }
      }
      continue;
    }

    const requestId = event.data.request_id as string | undefined;
    if (!requestId) continue;
    const request = requestById(requestId);

    if (event.node === "tool_workflow") {
      request.workflow = merge(request.workflow, event);
      continue;
    }
    const index = request.steps.findIndex((s) => s.node === event.node);
    if (index === -1) request.steps.push(merge(undefined, event));
    else request.steps[index] = merge(request.steps[index], event);
  }
  return reasoning;
}
