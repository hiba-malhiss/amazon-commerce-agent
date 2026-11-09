import type { SocketStatus } from "../../../api/chatSocket";
import type { ChatMessage } from "../../../hooks/useChat";
import { ChatHeader } from "../ChatHeader/ChatHeader";
import { ChatInput } from "../ChatInput/ChatInput";
import { MessageList } from "../MessageList/MessageList";
import { ServerAlert } from "../ServerAlert/ServerAlert";
import "./ChatPanel.css";

interface Props {
  title: string;
  messages: ChatMessage[];
  status: SocketStatus;
  sending: boolean;
  loadingHistory: boolean;
  error: string | null;
  onCloseError: () => void;
  onSend: (text: string) => void;
  eventsOpen: boolean;
  onToggleEvents: () => void;
}

export function ChatPanel(props: Props) {
  const { title, messages, status, sending, loadingHistory, error, onCloseError, onSend } = props;
  const canSend = !sending;

  return (
    <section className="chat-panel">
      <ChatHeader title={title} status={status} eventsOpen={props.eventsOpen} onToggleEvents={props.onToggleEvents} />
      <ServerAlert status={status} error={error} onCloseError={onCloseError} />
      <MessageList
        messages={messages}
        loading={loadingHistory}
        waiting={sending}
        canSend={canSend}
        onPickExample={onSend}
      />
      <ChatInput sending={sending} onSend={onSend} />
    </section>
  );
}
