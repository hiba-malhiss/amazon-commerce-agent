import { Badge } from "antd";
import type { SocketStatus } from "../../api/chatSocket";

const LABELS: Record<SocketStatus, { status: "success" | "processing" | "error"; text: string }> = {
  open: { status: "success", text: "Connected" },
  connecting: { status: "processing", text: "Connecting…" },
  closed: { status: "error", text: "Disconnected" },
};

export function ConnectionStatus({ status }: { status: SocketStatus }) {
  const { status: badge, text } = LABELS[status];
  return <Badge status={badge} text={text} />;
}
