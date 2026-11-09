import { MessageOutlined } from "@ant-design/icons";
import { Typography } from "antd";
import type { ThreadSummary } from "../../../api/types";
import { threadTitle } from "../../../hooks/useThreads";
import "./ThreadListItem.css";

interface Props {
  thread: ThreadSummary;
  active: boolean;
  onSelect: (id: string) => void;
}

export function ThreadListItem({ thread, active, onSelect }: Props) {
  return (
    <button
      type="button"
      className={`thread-item${active ? " thread-item--active" : ""}`}
      onClick={() => onSelect(thread.thread_id)}
      title={thread.thread_id}
    >
      <MessageOutlined />
      <Typography.Text ellipsis className="thread-item__title">
        {threadTitle(thread)}
      </Typography.Text>
    </button>
  );
}
