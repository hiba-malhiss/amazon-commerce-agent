import { ExclamationCircleOutlined, InfoCircleOutlined, LoadingOutlined, RobotOutlined, UserOutlined } from "@ant-design/icons";
import { Avatar } from "antd";
import type { ChatMessage } from "../../../hooks/useChat";
import { ItemCards } from "../ItemCards/ItemCards";
import { MessageText } from "../MessageText/MessageText";
import "./MessageBubble.css";

export function MessageBubble({ message }: { message: ChatMessage }) {
  if (message.role === "note") {
    return (
      <div className="note">
        <InfoCircleOutlined /> {message.text}
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
      </div>
    </div>
  );
}
