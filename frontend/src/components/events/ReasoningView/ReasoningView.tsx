import { Collapse, Descriptions, Tag, Typography } from "antd";
import type { ReactNode } from "react";
import type { TraceEvent } from "../../../api/types";
import { buildReasoning, type EventData, type RequestTrace, type Step, type StepState } from "./buildReasoning";
import "./ReasoningView.css";

interface Props {
  events: TraceEvent[];
}

const STATE_COLOR: Record<StepState, string> = { running: "processing", completed: "success", failed: "error" };

const OUTCOME_COLOR: Record<string, string> = {
  ready: "blue",
  success: "success",
  no_relevant_results: "warning",
  missing_info: "warning",
  needs_clarification: "warning",
  fail: "error",
};

const STEP_TITLE: Record<string, string> = {
  params_check: "Parameters check",
  api_call: "API call",
  rag_search: "Knowledge base search",
  missing_info: "Missing information",
};

function isEmpty(value: unknown): boolean {
  if (value === null || value === undefined || value === "") return true;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === "object") return Object.keys(value).length === 0;
  return false;
}

function formatValue(value: unknown): string {
  return typeof value === "object" && value !== null ? JSON.stringify(value) : String(value);
}

const code = (value: unknown) => <span className="reasoning__code">{formatValue(value)}</span>;
const tags = (values: unknown[], color?: string) => (
  <span className="reasoning__tags">
    {values.map((value, i) => (
      <Tag key={i} color={color}>
        {formatValue(value)}
      </Tag>
    ))}
  </span>
);
const outcomeTag = (status: string) => <Tag color={OUTCOME_COLOR[status]}>{status}</Tag>;
const duration = (data: EventData) => (typeof data.duration_ms === "number" ? `${data.duration_ms} ms` : undefined);
const pages = (start?: number | null, end?: number | null) =>
  start == null ? undefined : start === end ? `page ${start}` : `pages ${start}–${end}`;

// A parameters object as a small code / value table
function ParameterTable({ values }: { values: Record<string, unknown> }) {
  return (
    <table className="reasoning__params">
      <tbody>
        {Object.entries(values).map(([name, value]) => (
          <tr key={name}>
            <td className="reasoning__code">{name}</td>
            <td>{formatValue(value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Label / value rows; rows with no value are left out
function Details({ rows }: { rows: [string, unknown, ReactNode?][] }) {
  const items = rows
    .filter(([, value]) => !isEmpty(value))
    .map(([label, value, rendered]) => ({ key: label, label, children: rendered ?? formatValue(value) }));
  if (items.length === 0) return null;
  return <Descriptions size="small" column={1} bordered items={items} className="reasoning__details" />;
}

// One stage of the timeline: a dot coloured by its state, a title, and what it found
function Stage(props: { title: string; step?: Step; extra?: ReactNode; children?: ReactNode }) {
  const { title, step, extra, children } = props;
  const state = step?.state ?? "running";
  return (
    <li className={`reasoning__stage reasoning__stage--${state}`}>
      <div className="reasoning__stage-header">
        <span className="reasoning__stage-title">{title}</span>
        {extra}
        {step && <Tag color={STATE_COLOR[state]}>{state}</Tag>}
      </div>
      {step?.state === "failed" && <Typography.Text type="danger">{formatValue(step.data.error)}</Typography.Text>}
      {children}
    </li>
  );
}

function Understanding({ step }: { step: Step }) {
  const { data } = step;
  const requests = (data.requests ?? []) as EventData[];
  return (
    <>
      <Details
        rows={[
          ["Out of scope", data.out_of_scope ? "yes" : undefined, <Tag color="warning">yes</Tag>],
          ["Reason", data.out_of_scope_reason],
          [
            "Recent requests",
            data.recent_requests?.map((r: EventData) => r.id),
            tags(data.recent_requests?.map((r: EventData) => `${r.id} · ${r.request?.tool}`) ?? []),
          ],
          ["Understood", step.state === "completed" ? `${requests.length} request(s)` : undefined],
        ]}
      />
      {requests.map((request, i) => (
        <div key={i} className="reasoning__card">
          <div className="reasoning__card-title">Understood request {i + 1}</div>
          <Details
            rows={[
              ["Question", request.question],
              ["Tool", request.tool, code(request.tool)],
              ["Relation", request.relation, <Tag>{request.relation}</Tag>],
              ["Follow-up of", request.source_request_id, code(request.source_request_id)],
              ["Referenced entities", request.referenced_entities, tags(request.referenced_entities ?? [])],
              ["Reference quote", request.reference_quote, `“${request.reference_quote}”`],
              [
                "Extracted parameters",
                request.parameters,
                <ParameterTable
                  values={Object.fromEntries(
                    ((request.parameters ?? []) as EventData[]).map((p) => [
                      p.code,
                      p.operation === "remove" ? "(removed)" : p.value,
                    ]),
                  )}
                />,
              ],
            ]}
          />
        </div>
      ))}
    </>
  );
}

function ApiResults({ entities }: { entities: EventData[] }) {
  return (
    <Collapse
      size="small"
      items={[
        {
          key: "results",
          label: `Results (${entities.length})`,
          children: (
            <ol className="reasoning__results">
              {entities.map((entity) => (
                <li key={entity.reference}>
                  <div className="reasoning__card-title">
                    #{entity.position} {code(entity.reference)} <Tag>{entity.entity_code}</Tag>
                  </div>
                  <ParameterTable values={entity.attributes ?? {}} />
                </li>
              ))}
            </ol>
          ),
        },
      ]}
    />
  );
}

function RagChunks({ chunks, threshold }: { chunks: EventData[]; threshold: number | null }) {
  return (
    <Collapse
      size="small"
      items={chunks.map((chunk, i) => {
        const relevant = threshold == null || chunk.score >= threshold;
        return {
          key: i,
          label: (
            <span className={relevant ? "" : "reasoning__dropped"}>
              <Tag color={relevant ? "success" : "default"}>{chunk.score.toFixed(3)}</Tag>
              {chunk.filename}
              {chunk.section && ` › ${chunk.section}`}
            </span>
          ),
          children: (
            <>
              <Details
                rows={[
                  ["Chunk id", chunk.chunk_id, code(chunk.chunk_id)],
                  ["Pages", pages(chunk.page_start, chunk.page_end)],
                  ["Used in the reply", relevant ? "yes" : "no (below the threshold)"],
                ]}
              />
              <pre className="reasoning__content">{chunk.content}</pre>
            </>
          ),
        };
      })}
    />
  );
}

function StepDetails({ step }: { step: Step }) {
  const { data } = step;
  switch (step.node) {
    case "params_check":
      return (
        <Details
          rows={[
            ["Tool", data.tool, code(data.tool)],
            ["Missing", data.missing_parameters, tags(data.missing_parameters ?? [], "warning")],
            ["Next step", data.next_step, <Tag>{data.next_step}</Tag>],
          ]}
        />
      );
    case "api_call":
      return (
        <>
          <Details
            rows={[
              ["Integration", data.integration, code(data.integration)],
              ["Request", data.url, code(`${data.method} ${data.url}`)],
              ["Query params", data.query_params, <ParameterTable values={data.query_params ?? {}} />],
              [
                "Payload",
                data.payload,
                <pre className="reasoning__content">{JSON.stringify(data.payload, null, 2)}</pre>,
              ],
              [
                "HTTP status",
                data.status_code,
                <Tag color={data.status_code < 400 ? "success" : "error"}>{data.status_code}</Tag>,
              ],
              ["Duration", duration(data)],
              ["Results", Array.isArray(data.entities) ? String(data.entities.length) : undefined],
            ]}
          />
          {Array.isArray(data.entities) && data.entities.length > 0 && <ApiResults entities={data.entities} />}
        </>
      );
    case "rag_search":
      return (
        <>
          <Details
            rows={[
              ["Integration", data.integration, code(data.integration)],
              ["Knowledge base", data.knowledge_base, code(data.knowledge_base)],
              ["Query", data.query],
              ["Relevance threshold", data.relevance_threshold],
              ["Duration", duration(data)],
              [
                "Chunks",
                Array.isArray(data.chunks) ? data.chunks.length : undefined,
                Array.isArray(data.chunks)
                  ? `${data.chunks.length} found, ${data.chunks.filter((c: EventData) => data.relevance_threshold == null || c.score >= data.relevance_threshold).length} kept`
                  : undefined,
              ],
            ]}
          />
          {Array.isArray(data.chunks) && data.chunks.length > 0 && (
            <RagChunks chunks={data.chunks} threshold={data.relevance_threshold ?? null} />
          )}
        </>
      );
    case "missing_info":
      return (
        <Details
          rows={[["Ask the user for", data.missing_parameters, tags(data.missing_parameters ?? [], "warning")]]}
        />
      );
    default:
      return <Details rows={Object.entries(data).map(([label, value]) => [label, value])} />;
  }
}

function Request({ request, index, outcome }: { request: RequestTrace; index: number; outcome?: EventData }) {
  const resolution = request.resolution;
  const resolved = resolution?.request as EventData | undefined;
  const status: string | undefined = outcome?.status ?? request.workflow?.data.outcome ?? resolution?.status;
  return (
    <div className="reasoning__card">
      <div className="reasoning__card-title">
        Request {index + 1} {status && outcomeTag(status)}
      </div>
      <Details
        rows={[
          ["Request id", request.id, code(request.id)],
          ["Question", resolved?.question],
          ["Tool", resolved?.tool, code(resolved?.tool)],
          ["Relation", resolved?.relation, <Tag>{resolved?.relation}</Tag>],
          ["Follow-up of", resolved?.source_request_id, code(resolved?.source_request_id)],
          ["Referenced entities", resolved?.referenced_entities, tags(resolved?.referenced_entities ?? [])],
          ["Resolved parameters", resolved?.parameters, <ParameterTable values={resolved?.parameters ?? {}} />],
          ["Clarification asked", resolution?.status === "needs_clarification" ? resolution.error : undefined],
          ["Missing parameters", outcome?.missing_parameters, tags(outcome?.missing_parameters ?? [], "warning")],
          ["Error", outcome?.error ?? (request.workflow?.state === "failed" ? request.workflow.data.error : undefined)],
        ]}
      />
      {request.steps.length > 0 && (
        <ol className="reasoning__timeline reasoning__timeline--nested">
          {request.steps.map((step) => (
            <Stage key={step.node} title={STEP_TITLE[step.node] ?? step.node} step={step}>
              <StepDetails step={step} />
            </Stage>
          ))}
        </ol>
      )}
    </div>
  );
}

// The message's events as the agent's reasoning: what it understood, what it did per request, how it replied
export function ReasoningView({ events }: Props) {
  const { understand, resolve, requests, collect, respond } = buildReasoning(events);
  const outcomes = (collect?.data.outcomes ?? []) as EventData[];
  const outcomeById = new Map(outcomes.map((o) => [o.id, o]));
  const visibleLists = (collect?.data.visible_entities ?? []) as EventData[];

  return (
    <ol className="reasoning__timeline">
      {understand && (
        <Stage title="Understanding" step={understand}>
          <Understanding step={understand} />
        </Stage>
      )}
      {resolve && (
        <Stage title="Requests" step={resolve} extra={<Tag>{requests.length}</Tag>}>
          {requests.map((request, i) => (
            <Request key={request.id} request={request} index={i} outcome={outcomeById.get(request.id)} />
          ))}
        </Stage>
      )}
      {collect && (
        <Stage title="Collect" step={collect}>
          <Details
            rows={[
              ["Outcomes", outcomes, tags(outcomes.map((o) => `${o.id} · ${o.status}`))],
              [
                "Stored entities",
                Object.keys(collect.data.entities ?? {}),
                String(Object.keys(collect.data.entities ?? {}).length),
              ],
              [
                "Visible card lists",
                visibleLists,
                <ol className="reasoning__results">
                  {visibleLists.map((list, i) => (
                    <li key={i}>{tags((list.items ?? []).map((item: EventData) => item.reference))}</li>
                  ))}
                </ol>,
              ],
            ]}
          />
        </Stage>
      )}
      {respond && <Stage title="Response" step={respond} />}
    </ol>
  );
}
