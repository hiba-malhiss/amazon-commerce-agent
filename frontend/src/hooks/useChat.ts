import { useCallback, useEffect, useRef, useState } from "react";
import { ChatSocket, type SocketStatus } from "../api/chatSocket";
import { getThreadMessages } from "../api/threads";
import type { ChatEvent, MessageResponse, PromptEvent, TraceEvent } from "../api/types";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "note";
  text: string;
  entities: string[];
  pending?: boolean;
  failed?: boolean;
}

function fromResponse(m: MessageResponse): ChatMessage {
  return {
    id: m.context.message_id,
    role: m.context.role,
    text: m.body.text,
    entities: m.body.entities,
  };
}

interface Options {
  threadId: string | null;
  // Called when the backend created the thread for us (we sent thread_id: null)
  onThreadCreated: (threadId: string) => void;
  // A reply arrived: the backend may have named the thread (its first message)
  onReplied: (threadId: string) => void;
}

// Several searches + one LLM reply; give up waiting after this
const REPLY_TIMEOUT_MS = 120_000;

export function useChat({ threadId, onThreadCreated, onReplied }: Options) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [socketStatus, setSocketStatus] = useState<SocketStatus>("connecting");
  const [sending, setSending] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [liveTrace, setLiveTrace] = useState<TraceEvent[]>([]);
  const liveTraceRef = useRef<TraceEvent[]>([]);
  const [livePrompts, setLivePrompts] = useState<PromptEvent[]>([]);

  const socketRef = useRef<ChatSocket | null>(null);
  const timeoutRef = useRef<number | undefined>(undefined); // set it after sending a message clear it when an event arrive this is to display error if it takes too long to respond
  const sendingRef = useRef(false);
  const threadRef = useRef(threadId);
  sendingRef.current = sending;
  const skipNextLoad = useRef<string | null>(null);
  const callbacks = useRef({ onThreadCreated, onReplied });
  callbacks.current = { onThreadCreated, onReplied };
  threadRef.current = threadId;

  const handleEvent = useCallback((event: ChatEvent) => {
    if (event.type === "trace") {
      liveTraceRef.current = [...liveTraceRef.current, event.data];
      setLiveTrace(liveTraceRef.current);
      return;
    }
    if (event.type === "prompt") {
      setLivePrompts((prev) => [...prev, event.data]);
      return;
    }
    window.clearTimeout(timeoutRef.current);
    setSending(false);

    if (event.type === "error") {
      setError(
        event.message === "Invalid message format"
          ? "The message couldn't be sent: it's empty or too long."
          : event.message,
      );
      setMessages((prev) => prev.map((m) => (m.pending ? { ...m, pending: false, failed: true } : m)));
      return;
    }

    const { data } = event;
    const isNewThread = threadRef.current === null;
    if (!isNewThread && data.thread_id !== threadRef.current) return; // user switched threads

    if (isNewThread) {
      skipNextLoad.current = data.thread_id; // we already have its messages
      callbacks.current.onThreadCreated(data.thread_id);
    }

    callbacks.current.onReplied(data.thread_id);

    setMessages((prev) => {
      const next = prev.filter((m) => !m.pending);
      next.push(fromResponse(data.user_message));
      next.push(
        data.assistant_message
          ? fromResponse(data.assistant_message)
          : {
              id: `note-${data.interaction_id}`,
              role: "note",
              text: "The agent handled your message but didn't send a reply.",
              entities: [],
            },
      );
      return next;
    });
  }, []);

  // One socket for the whole app
  useEffect(() => {
    const onStatus = (next: SocketStatus) => {
      setSocketStatus(next);
      if (next === "closed" && sendingRef.current) {
        window.clearTimeout(timeoutRef.current);
        setSending(false);
        setError("Connection lost before the reply arrived. Please try again.");
        setMessages((prev) => prev.map((m) => (m.pending ? { ...m, pending: false, failed: true } : m)));
      }
    };
    const socket = new ChatSocket({ onEvent: handleEvent, onStatus });
    socketRef.current = socket;
    socket.connect();
    return () => {
      socket.close();
      window.clearTimeout(timeoutRef.current);
    };
  }, [handleEvent]);

  // Load history whenever the active thread changes
  useEffect(() => {
    setError(null);
    setSending(false);
    if (!threadId) {
      setMessages([]);
      return;
    }
    if (skipNextLoad.current === threadId) {
      skipNextLoad.current = null;
      return;
    }
    let cancelled = false;
    setMessages([]);
    setLoadingHistory(true);
    getThreadMessages(threadId)
      .then((res) => {
        if (cancelled) return;
        setMessages(res.messages.map(fromResponse));
      })
      .catch((e: Error) => !cancelled && setError(`Couldn't load history: ${e.message}`))
      .finally(() => !cancelled && setLoadingHistory(false));
    return () => {
      cancelled = true;
    };
  }, [threadId]);

  const send = useCallback(
    (text: string) => {
      const message = text.trim();
      if (!message || sending) return;
      setError(null);
      liveTraceRef.current = [];
      setLiveTrace([]);
      setLivePrompts([]);
      setMessages((prev) => [
        ...prev,
        { id: `pending-${Date.now()}`, role: "user", text: message, entities: [], pending: true },
      ]);
      const ok = socketRef.current?.send({ type: "message", thread_id: threadId, message });
      if (ok) {
        setSending(true);
        window.clearTimeout(timeoutRef.current);
        timeoutRef.current = window.setTimeout(() => {
          setSending(false);
          setError("The agent is taking too long. Please try again.");
          setMessages((prev) => prev.map((m) => (m.pending ? { ...m, pending: false, failed: true } : m)));
        }, REPLY_TIMEOUT_MS);
      } else {
        setError("Not connected to the server.");
        setMessages((prev) => prev.map((m) => (m.pending ? { ...m, pending: false, failed: true } : m)));
      }
    },
    [sending, threadId],
  );

  return {
    messages,
    socketStatus,
    sending,
    liveTrace,
    livePrompts,
    loadingHistory,
    error,
    clearError: () => setError(null),
    send,
  };
}
