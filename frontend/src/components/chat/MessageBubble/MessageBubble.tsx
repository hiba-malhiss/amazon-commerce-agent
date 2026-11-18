import {
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  LoadingOutlined,
  RobotOutlined,
  ThunderboltOutlined,
  UserOutlined,
} from "@ant-design/icons";
import { Avatar, Button } from "antd";
import { useSetAtom } from "jotai";
import { useSearchParams } from "react-router-dom";
import type { ChatMessage } from "../../../hooks/useChat";
import { eventsOpenAtom } from "../../../state/atoms";
import { ItemCards } from "../ItemCards/ItemCards";
import { MessageText } from "../MessageText/MessageText";
import "./MessageBubble.css";

export function MessageBubble({ message }: { message: ChatMessage }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const setEventsOpen = useSetAtom(eventsOpenAtom);

  const canViewEvents = !!message.interactionId && !message.pending && !message.failed;
  const selected = !!message.interactionId && message.interactionId === searchParams.get("interaction");

  const viewEvents = () => {
    const id = message.interactionId!;
    setSearchParams(
      (prev) => {
        const next = new URLSearchParams(prev);
        next.set("interaction", id);
        return next;
      },
      { replace: true },
    );
    setEventsOpen(true);
  };

  const eventsButton = canViewEvents && (
    <Button
      type={selected ? "primary" : "text"}
      size="small"
      ghost={selected}
      className={`msg__events${selected ? " msg__events--active" : ""}`}
      icon={<ThunderboltOutlined />}
      onClick={viewEvents}
    >
      Events
    </Button>
  );

  if (message.role === "note") {
    return (
      <div className="note">
        <InfoCircleOutlined /> {message.text} {eventsButton}
      </div>
    );
  }

  const isUser = message.role === "user";
  return (
    <div className={`msg msg--${message.role}`}>
      <Avatar className="msg__avatar" icon={isUser ? <UserOutlined /> : <RobotOutlined />} />
      <div className="msg__body">
        <div className={`bubble${message.failed ? " bubble--failed" : ""}`}>
          <MessageText text={message.text} markdown={!isUser} />
          {message.pending && (
            <span className="bubble__meta">
              <LoadingOutlined /> Sending…
            </span>
          )}
          {message.failed && (
            <span className="bubble__meta">
              <ExclamationCircleOutlined /> Not delivered
            </span>
          )}
        </div>
        {message.entities.length > 0 && <ItemCards cards={message.entities} />}
        {!isUser && eventsButton}
      </div>
    </div>
  );
}
