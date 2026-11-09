# Frontend

React + TypeScript + Vite + [antd](https://ant.design). A simple chat for the backend.

```bash
npm install
npm run dev        # http://localhost:5173 (backend must run on :8000)
npm run build
```

The Vite dev server proxies `/threads`, `/health` and the `/ws` WebSocket to `localhost:8000`, so the backend needs no CORS setup.

## Structure

```
src/
  api/           types.ts (mirrors backend schemas) · threads.ts (REST) · chatSocket.ts (WebSocket + reconnect)
  hooks/         useThreads.ts (sidebar list from GET /threads) · useUrlThreadId.ts (/chat/<id>) · useChat.ts (history, send, replies)
  components/
    sidebar/     ThreadSidebar · NewThreadButton · ThreadList · ThreadListItem
    chat/        ChatPanel · ChatHeader · ConnectionStatus · ServerAlert · MessageList · MessageBubble
                 · MessageText (Markdown) · EntityTags (Amazon links) · TypingIndicator · EmptyChat · ChatInput
    events/      EventsPanel (trace events as collapsible JSON, react-json-view-lite)
```

A component with its own styles lives in a folder named after it, next to its CSS
(`chat/MessageBubble/MessageBubble.tsx` + `MessageBubble.css`). A component without styles
is a single file (`chat/ConnectionStatus.tsx`).
