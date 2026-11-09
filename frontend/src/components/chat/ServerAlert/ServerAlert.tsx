import { Alert } from "antd";
import type { SocketStatus } from "../../../api/chatSocket";
import "./ServerAlert.css";

interface Props {
  status: SocketStatus;
  error: string | null;
  onCloseError: () => void;
}

export function ServerAlert({ status, error, onCloseError }: Props) {
  if (status === "closed") {
    return (
      <div className="column">
        <Alert
          className="chat-alert"
          type="warning"
          showIcon
          message="Can't reach the backend"
          description="Start it on http://127.0.0.1:8000 (uvicorn app.main:app). The chat reconnects by itself."
        />
      </div>
    );
  }
  if (!error) return null;
  return (
    <div className="column">
      <Alert className="chat-alert" type="error" showIcon message={error} closable onClose={onCloseError} />
    </div>
  );
}
