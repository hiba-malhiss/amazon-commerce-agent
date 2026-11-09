import { Button, Typography } from "antd";
import type { ThreadSummary } from "../../../api/types";
import { ThreadList } from "../ThreadList/ThreadList";
import "./ThreadSidebar.css";
import { PlusOutlined } from "@ant-design/icons";

interface Props {
  threads: ThreadSummary[];
  activeId: string | null;
  hasMore: boolean;
  loadingMore: boolean;
  onLoadMore: () => void;
  creating: boolean;
  onCreate: () => void;
  onSelect: (id: string) => void;
}

export function ThreadSidebar(props: Props) {
  const { threads, activeId, hasMore, loadingMore, onLoadMore, creating, onCreate, onSelect } = props;
  return (
    <div className="sidebar">
      <Typography.Title level={5} className="sidebar__brand">
        🛒 Commerce Agent
      </Typography.Title>
      <Button type="primary" icon={<PlusOutlined />} block loading={creating} onClick={onCreate}>
        New thread
      </Button>
      {threads.length > 0 && <div className="sidebar__section">Recent</div>}
      <ThreadList
        threads={threads}
        activeId={activeId}
        hasMore={hasMore}
        loadingMore={loadingMore}
        onLoadMore={onLoadMore}
        onSelect={onSelect}
      />
    </div>
  );
}
