import { Collapse, Typography } from "antd";
import { useEffect, useRef } from "react";
import type { PromptEvent } from "../../../api/types";
import "./PromptsPanel.css";

interface Props {
  prompts: PromptEvent[];
}

// First line of the prompt, skipping role labels like "[system]"
function preview(prompt: string): string {
  return prompt.split("\n").find((line) => line.trim() && !/^\[\w+\]$/.test(line.trim())) ?? "";
}

export function PromptsPanel({ prompts }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [prompts.length]);

  if (prompts.length === 0) {
    return <Typography.Text type="secondary">Send a message to see the prompts.</Typography.Text>;
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
              <span className="prompts__preview">{preview(p.prompt)}</span>
            </span>
          ),
          children: <pre className="prompts__content">{p.prompt}</pre>,
        }))}
      />
      <div ref={bottomRef} />
    </div>
  );
}
