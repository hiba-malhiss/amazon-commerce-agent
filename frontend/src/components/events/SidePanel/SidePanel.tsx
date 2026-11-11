import { CloseOutlined } from "@ant-design/icons";
import { Button, Tabs } from "antd";
import type { PromptEvent, TraceEvent } from "../../../api/types";
import { EventsPanel } from "../EventsPanel/EventsPanel";
import { PromptsPanel } from "../PromptsPanel/PromptsPanel";
import "./SidePanel.css";

interface Props {
  events: TraceEvent[];
  prompts: PromptEvent[];
  onClose: () => void;
}

export function SidePanel({ events, prompts, onClose }: Props) {
  return (
    <aside className="side-panel">
      <Tabs
        size="small"
        items={[
          {
            key: "events",
            label: `Events (${events.length})`,
            children: <div className="side-panel__body"><EventsPanel events={events} /></div>,
          },
          {
            key: "prompts",
            label: `Prompts (${prompts.length})`,
            children: <div className="side-panel__body"><PromptsPanel prompts={prompts} /></div>,
          },
        ]}
        tabBarExtraContent={
          <Button size="small" type="text" icon={<CloseOutlined />} onClick={onClose} aria-label="Close panel" />
        }
      />
    </aside>
  );
}
