import { Button, Typography } from "antd";
import { useEffect, useRef, useState } from "react";
import type { TraceEvent } from "../../../api/types";
import { JsonView, defaultStyles } from "react-json-view-lite";
import "react-json-view-lite/dist/index.css";
import "./EventsPanel.css";

interface Props {
  events: TraceEvent[];
}

export function EventsPanel({ events }: Props) {
  const [openDepth, setOpenDepth] = useState(2);
  const [version, setVersion] = useState(0);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ block: "end" });
  }, [events.length]);

  const setAll = (depth: number) => {
    setOpenDepth(depth);
    setVersion((v) => v + 1);
  };

  return (
    <div className="events">
      {events.length > 0 && (
        <div className="events__actions">
          <Button size="small" type="text" onClick={() => setAll(Infinity)}>
            Expand all
          </Button>
          <Button size="small" type="text" onClick={() => setAll(0)}>
            Collapse all
          </Button>
        </div>
      )}
      <div>
        {events.length === 0 ? (
          <Typography.Text type="secondary">Send a message to see the agent's events.</Typography.Text>
        ) : (
          <div key={version}>
            {events.map((event, i) => (
              <div className={`events__item events__item--${event.status}`} key={i}>
                <div className="events__title">
                  {event.node} · {event.status}
                </div>
                <JsonView
                  data={event}
                  style={defaultStyles}
                  // level 0 = the event, 1 = its data, deeper values start folded
                  shouldExpandNode={(level) => level < openDepth}
                />
              </div>
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
