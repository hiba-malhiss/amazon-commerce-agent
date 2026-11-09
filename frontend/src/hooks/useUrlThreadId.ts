import { useCallback, useEffect, useState } from "react";

// The active thread lives in the URL: /chat/<thread-id>
const PATTERN = /^\/chat\/([0-9a-f-]{36})\/?$/i;

function readFromUrl(): string | null {
  return window.location.pathname.match(PATTERN)?.[1] ?? null;
}

export function threadPath(id: string | null): string {
  return id ? `/chat/${id}` : "/";
}

// The app has one route with one value, so I wrote a small hook instead of adding a router.
export function useUrlThreadId() {
  const [threadId, setThreadId] = useState<string | null>(readFromUrl);

  useEffect(() => {
    // set the new thread id when navigate back
    const onPop = () => setThreadId(readFromUrl());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const navigate = useCallback((id: string | null, { replace = false } = {}) => {
    const path = threadPath(id);
    if (window.location.pathname !== path) {
      window.history[replace ? "replaceState" : "pushState"](null, "", path);
    }
    setThreadId(id);
  }, []);

  return [threadId, navigate] as const;
}
