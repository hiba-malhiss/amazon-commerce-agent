import { ArrowUpOutlined } from "@ant-design/icons";
import { Button, Input } from "antd";
import { useState } from "react";
import { MAX_MESSAGE_LENGTH } from "../../../config";
import "./ChatInput.css";

interface Props {
  sending: boolean;
  onSend: (text: string) => void;
}

export function ChatInput({ sending, onSend }: Props) {
  const [text, setText] = useState("");

  const submit = () => {
    if (!text.trim() || sending) return;
    onSend(text);
    setText("");
  };

  return (
    <div className="chat-input column">
      <div className="chat-input__box">
        <Input.TextArea
          variant="borderless"
          value={text}
          onChange={(e) => setText(e.target.value.slice(0, MAX_MESSAGE_LENGTH))}
          onPressEnter={(e) => {
            if (!e.shiftKey) {
              e.preventDefault();
              submit();
            }
          }}
          placeholder="Ask about a product…"
          autoSize={{ minRows: 1, maxRows: 6 }}
          maxLength={MAX_MESSAGE_LENGTH}
          showCount={text.length > MAX_MESSAGE_LENGTH * 0.8}
        />
        <Button
          type="primary"
          shape="circle"
          icon={<ArrowUpOutlined />}
          onClick={submit}
          loading={sending}
          disabled={!text.trim()}
          aria-label="Send"
        />
      </div>
      <div className="chat-input__hint">Enter to send · Shift+Enter for a new line</div>
    </div>
  );
}
