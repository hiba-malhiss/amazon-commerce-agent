import { App as AntApp, Layout, Splitter } from "antd";
import { useEffect, useState } from "react";
import { ChatPanel } from "./components/chat/ChatPanel/ChatPanel";
import { SidePanel } from "./components/events/SidePanel/SidePanel";
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
              onSend={chat.send}
              eventsOpen={eventsOpen}
              onToggleEvents={() => setEventsOpen((open) => !open)}
            />
          </Splitter.Panel>
          {eventsOpen && (
            <Splitter.Panel defaultSize={420} min={320} max="75%">
              <SidePanel events={chat.liveTrace} prompts={chat.livePrompts} onClose={() => setEventsOpen(false)} />
            </Splitter.Panel>
          )}
        </Splitter>
      </Layout.Content>
    </Layout>
  );
}
