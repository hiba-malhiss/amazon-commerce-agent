import { CodeOutlined } from "@ant-design/icons";
import { Button, Typography } from "antd";
import type { SocketStatus } from "../../../api/chatSocket";
import { ConnectionStatus } from "../ConnectionStatus";
import "./ChatHeader.css";

interface Props {
  title: string;
  status: SocketStatus;
  eventsOpen: boolean;
  onToggleEvents: () => void;
}

export function ChatHeader({ title, status, eventsOpen, onToggleEvents }: Props) {
  return (
    <header className="chat-header">
      <div className="column">
        <Typography.Title level={5} ellipsis className="chat-header__title">
          {title}
        </Typography.Title>
        <span className="chat-header__right">
          <ConnectionStatus status={status} />
          <Button size="small" icon={<CodeOutlined />} type={eventsOpen ? "primary" : "default"} onClick={onToggleEvents}>
            Events
          </Button>
        </span>
      </div>
    </header>
  );
}
