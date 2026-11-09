import { Empty, Spin } from "antd";
import { useEffect, useRef } from "react";
import type { ThreadSummary } from "../../../api/types";
import { ThreadListItem } from "../ThreadListItem/ThreadListItem";
import "./ThreadList.css";

interface Props {
  threads: ThreadSummary[];
  activeId: string | null;
  hasMore: boolean;
  loadingMore: boolean;
  onLoadMore: () => void;
  onSelect: (id: string) => void;
}

export function ThreadList({ threads, activeId, hasMore, loadingMore, onLoadMore, onSelect }: Props) {
  const listRef = useRef<HTMLElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  // Load the next page when the end of the list scrolls into view
  useEffect(() => {
    const end = endRef.current;
    if (!end || !hasMore) return;
    const observer = new IntersectionObserver(
      (entries) => entries[0].isIntersecting && onLoadMore(),
      { root: listRef.current, rootMargin: "120px" },
    );
    observer.observe(end);
    return () => {
      observer.disconnect()
    };
  }, [hasMore, onLoadMore, threads.length]);

  if (threads.length === 0) {
    return <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description="No threads yet" />;
  }

  return (
    <nav className="thread-list" ref={listRef}>
      {threads.map((t) => (
        <ThreadListItem key={t.thread_id} thread={t} active={t.thread_id === activeId} onSelect={onSelect} />
      ))}
      {hasMore && (
        <div ref={endRef} className="thread-list__end">
          {loadingMore && <Spin size="small" />}
        </div>
      )}
    </nav>
  );
}
