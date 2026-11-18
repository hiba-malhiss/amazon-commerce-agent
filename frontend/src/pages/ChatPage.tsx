import { App as AntApp, Layout as AntLayout, Splitter } from "antd";
import { useAtom } from "jotai";
import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { getInteractionTrace, type InteractionTrace } from "../api/threads";
import { ChatPanel } from "../components/chat/ChatPanel/ChatPanel";
import { SidePanel } from "../components/events/SidePanel/SidePanel";
import { ThreadSidebar } from "../components/sidebar/ThreadSidebar/ThreadSidebar";
import { useChat } from "../hooks/useChat";
import { threadTitle, useThreads } from "../hooks/useThreads";
import { eventsOpenAtom } from "../state/atoms";

export function ChatPage() {
  const { message } = AntApp.useApp();
  const navigate = useNavigate();
  const { threadId } = useParams(); // from /chat/:threadId ("/" has none)
  const activeId = threadId ?? null;
  const [searchParams, setSearchParams] = useSearchParams(); // ?interaction=<id>
  const interactionId = searchParams.get("interaction");
  const [eventsOpen, setEventsOpen] = useAtom(eventsOpenAtom);
  const [viewedTrace, setViewedTrace] = useState<InteractionTrace | null>(null);
  const { threads, hasMore, loadingMore, loadMore, creating, createNewThread, refresh, error } = useThreads();

  const setInteraction = useCallback(
    (id: string | null) => {
      setSearchParams(
        (prev) => {
          const next = new URLSearchParams(prev);
          if (id) next.set("interaction", id);
          else next.delete("interaction");
          return next;
        },
        { replace: true },
      );
    },
    [setSearchParams],
  );

  const chat = useChat({
    threadId: activeId,
    onThreadCreated: (id) => navigate(`/chat/${id}`, { replace: true }),
    // The first reply titles the thread; a thread with no title yet needs one reload
    onReplied: (id) => {
      if (!threads.find((t) => t.thread_id === id)?.title) void refresh();
    },
  });

  useEffect(() => {
    if (error) message.error(`Couldn't load threads: ${error}`);
  }, [error, message]);

  const liveInteractionId = chat.liveTrace[0]?.interaction_id;
  const lastInteractionId = [...chat.messages].reverse().find((m) => m.interactionId)?.interactionId;

  // Default to the last interaction (once a turn isn't streaming); a shared ?interaction= link is kept
  useEffect(() => {
    if (!interactionId && lastInteractionId && !chat.sending) setInteraction(lastInteractionId);
  }, [interactionId, lastInteractionId, chat.sending, setInteraction]);

  // A past interaction uses its saved trace; the current one uses the live trace
  useEffect(() => {
    if (!interactionId || interactionId === liveInteractionId) {
      setViewedTrace(null);
      return;
    }
    let cancelled = false;
    getInteractionTrace(interactionId)
      .then((trace) => !cancelled && setViewedTrace(trace))
      .catch((e: Error) => {
        if (!cancelled) {
          setViewedTrace({ events: [], prompts: [] });
          message.error(`Couldn't load events: ${e.message}`);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [interactionId, liveInteractionId, message]);

  const handleCreate = () => {
    createNewThread()
      .then((id) => navigate(`/chat/${id}`))
      .catch((e: Error) => message.error(`Couldn't create a thread: ${e.message}`));
  };

  // Sending a new message follows the live turn again (drops the selected interaction)
  const handleSend = (text: string) => {
    setInteraction(null);
    chat.send(text);
  };

  const title = threadTitle(threads.find((t) => t.thread_id === activeId));

  return (
    <>
      <AntLayout.Sider width={260} theme="light" className="app__sider">
        <ThreadSidebar
          threads={threads}
          activeId={activeId}
          hasMore={hasMore}
          loadingMore={loadingMore}
          onLoadMore={loadMore}
          creating={creating}
          onCreate={handleCreate}
          onSelect={(id) => navigate(`/chat/${id}`)}
        />
      </AntLayout.Sider>
      <AntLayout.Content className="app__content">
        <Splitter>
          <Splitter.Panel min={360}>
            <ChatPanel
              title={title}
              messages={chat.messages}
              status={chat.socketStatus}
              sending={chat.sending}
              loadingHistory={chat.loadingHistory}
              error={chat.error}
              onCloseError={chat.clearError}
              onSend={handleSend}
              eventsOpen={eventsOpen}
              onToggleEvents={() => setEventsOpen((open) => !open)}
            />
          </Splitter.Panel>
          {eventsOpen && (
            <Splitter.Panel defaultSize={420} min={320} max="75%">
              <SidePanel
                events={viewedTrace?.events ?? chat.liveTrace}
                prompts={viewedTrace?.prompts ?? chat.livePrompts}
                onClose={() => setEventsOpen(false)}
              />
            </Splitter.Panel>
          )}
        </Splitter>
      </AntLayout.Content>
    </>
  );
}
