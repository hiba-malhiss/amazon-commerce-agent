import { Spin } from "antd";
import { useEffect, useRef } from "react";
import type { ChatMessage } from "../../../hooks/useChat";
import { EmptyChat } from "../EmptyChat/EmptyChat";
import { MessageBubble } from "../MessageBubble/MessageBubble";
import { TypingIndicator } from "../TypingIndicator/TypingIndicator";
import "./MessageList.css";

interface Props {
  messages: ChatMessage[];
  loading: boolean;
  waiting: boolean;
  canSend: boolean;
  onPickExample: (text: string) => void;
}

export function MessageList({ messages, loading, waiting, canSend, onPickExample }: Props) {
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, waiting]);

  if (loading) {
    return (
      <div className="message-list message-list--center">
        <Spin />
      </div>
    );
  }
  if (messages.length === 0) return <EmptyChat onPick={onPickExample} disabled={!canSend} />;

  return (
    <div className="message-list">
      <div className="column">
        {messages.map((m) => (
          <MessageBubble key={m.id} message={m} />
        ))}
        {waiting && <TypingIndicator />}
        <div ref={endRef} />
      </div>
    </div>
  );
}
