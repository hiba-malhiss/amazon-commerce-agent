import { Collapse, Typography } from "antd";
import { useEffect, useRef } from "react";
import type { PromptEvent } from "../../../api/types";
import "./PromptsPanel.css";

interface Props {
  prompts: PromptEvent[];
}

export function PromptsPanel({ prompts }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [prompts.length]);

  if (prompts.length === 0) {
    return <Typography.Text type="secondary">Send a message to see the system prompts.</Typography.Text>;
  }
  return (
    <div className="prompts">
      <Collapse
        size="small"
        items={prompts.map((p, i) => ({
          key: i,
          label: (
            <span className="prompts__label">
              <b>{p.node}</b>
              <span className="prompts__preview">{p.prompt.trim().split("\n")[0]}</span>
            </span>
          ),
          children: <pre className="prompts__content">{p.prompt}</pre>,
        }))}
      />
      <div ref={bottomRef} />
    </div>
  );
}
