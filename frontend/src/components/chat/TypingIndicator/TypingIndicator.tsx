import { RobotOutlined } from "@ant-design/icons";
import { Avatar } from "antd";
import "../MessageBubble/MessageBubble.css";
import "./TypingIndicator.css";

// Shown while the agent works (its events appear in the Events panel)
export function TypingIndicator() {
  return (
    <div className="msg msg--assistant" aria-live="polite">
      <Avatar className="msg__avatar" icon={<RobotOutlined />} />
      <div className="bubble typing">
        <span className="typing__dots">
          <i />
          <i />
          <i />
        </span>
        <span className="typing__text">Searching…</span>
      </div>
    </div>
  );
}
