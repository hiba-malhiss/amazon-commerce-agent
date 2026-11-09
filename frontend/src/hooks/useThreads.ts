import { useCallback, useEffect, useRef, useState } from "react";
import { createThread, listThreads } from "../api/threads";
import type { ThreadSummary } from "../api/types";
import { useUrlThreadId } from "./useUrlThreadId";

export const DEFAULT_TITLE = "New chat";

export function threadTitle(thread: ThreadSummary | undefined): string {
  return thread?.title ?? DEFAULT_TITLE;
}

export function useThreads() {
  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [hasMore, setHasMore] = useState(false);
  const [loadingMore, setLoadingMore] = useState(false);
  const [activeId, setActiveId] = useUrlThreadId();
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const loadingRef = useRef(false);
  const threadsRef = useRef<ThreadSummary[]>([]);
  threadsRef.current = threads;

  // load the first page on load and on creating a new thread
  const refresh = useCallback(async () => {
    try {
      const page = await listThreads();
      setThreads((prev) => {
        const fresh = new Set(page.threads.map((t) => t.thread_id));
        return [...page.threads, ...prev.filter((t) => !fresh.has(t.thread_id))];
      });
      // Once older pages are loaded, their has_more is the one that counts
      setHasMore((more) => (threadsRef.current.length > page.threads.length ? more : page.has_more));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  // Next page, when the end of the list scrolls into view
  const loadMore = useCallback(async () => {
    if (!hasMore || loadingRef.current) return;
    loadingRef.current = true;
    setLoadingMore(true);
    try {
      // Offset = threads already shown. A thread created meanwhile shifts the list by one;
      // the duplicate it causes is filtered out below
      const page = await listThreads(threadsRef.current.length);
      setThreads((prev) => {
        const shown = new Set(prev.map((t) => t.thread_id));
        return [...prev, ...page.threads.filter((t) => !shown.has(t.thread_id))];
      });
      setHasMore(page.has_more);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      loadingRef.current = false;
      setLoadingMore(false);
    }
  }, [hasMore]);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  const createNewThread = useCallback(async () => {
    setCreating(true);
    try {
      const { thread_id } = await createThread();
      setActiveId(thread_id);
      await refresh();
    } finally {
      setCreating(false);
    }
  }, [refresh, setActiveId]);

  return {
    threads,
    hasMore,
    loadingMore,
    loadMore,
    activeId,
    setActiveId,
    creating,
    createNewThread,
    refresh,
    error,
  };
}
