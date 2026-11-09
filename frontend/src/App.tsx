import { App as AntApp, Layout } from "antd";
import { useEffect, useState } from "react";
import { ChatPanel } from "./components/chat/ChatPanel/ChatPanel";
import { EventsPanel } from "./components/events/EventsPanel/EventsPanel";
import { ThreadSidebar } from "./components/sidebar/ThreadSidebar/ThreadSidebar";
import { useChat } from "./hooks/useChat";
import { threadTitle, useThreads } from "./hooks/useThreads";
import "./App.css";

export default function App() {
  const { message } = AntApp.useApp();
  const [eventsOpen, setEventsOpen] = useState(true);
  const { threads, hasMore, loadingMore, loadMore, activeId, setActiveId, creating, createNewThread, refresh, error } =
    useThreads();

  const chat = useChat({
    threadId: activeId,
    // when sending a message without thread id the BE creates one
    onThreadCreated: (id) => setActiveId(id, { replace: true }), // "/" becomes /chat/<id>, no extra history entry
    // Only the first reply matters: the backend titles the thread from its first message.
    // A thread with no title yet (or not in the list: started from "/") needs one reload
    onReplied: (id) => {
      if (!threads.find((t) => t.thread_id === id)?.title) void refresh();
    },
  });

  useEffect(() => {
    if (error) message.error(`Couldn't load threads: ${error}`);
  }, [error, message]);

  const handleCreate = () => {
    createNewThread().catch((e: Error) => message.error(`Couldn't create a thread: ${e.message}`));
  };

  const title = threadTitle(threads.find((t) => t.thread_id === activeId));

  return (
    <Layout className="app">
      <Layout.Sider width={260} theme="light" className="app__sider">
        <ThreadSidebar
          threads={threads}
          activeId={activeId}
          hasMore={hasMore}
          loadingMore={loadingMore}
          onLoadMore={loadMore}
          creating={creating}
          onCreate={handleCreate}
          onSelect={(id) => setActiveId(id)}
        />
      </Layout.Sider>
      <Layout.Content className="app__content">
        <ChatPanel
          title={title}
          messages={chat.messages}
          status={chat.socketStatus}
          sending={chat.sending}
          loadingHistory={chat.loadingHistory}
          error={chat.error}
          onCloseError={chat.clearError}
          onSend={chat.send}
          eventsOpen={eventsOpen}
          onToggleEvents={() => setEventsOpen((open) => !open)}
        />
      </Layout.Content>
      <Layout.Sider
        width={420}
        collapsedWidth={0}
        collapsed={!eventsOpen}
        trigger={null}
        theme="light"
        className="app__events"
      >
        <EventsPanel events={chat.liveTrace} onClose={() => setEventsOpen(false)} />
      </Layout.Sider>
    </Layout>
  );
}
