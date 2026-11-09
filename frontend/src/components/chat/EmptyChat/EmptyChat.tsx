import { Button, Typography } from "antd";
import "./EmptyChat.css";

const EXAMPLES = [
  "Find Samsung headphones under $100",
  "Show me running shoes for women",
  "Cheapest 1TB SSD from a known brand",
];

interface Props {
  onPick: (text: string) => void;
  disabled: boolean;
}

export function EmptyChat({ onPick, disabled }: Props) {
  return (
    <div className="empty-chat">
      <div className="empty-chat__inner">
        <div className="empty-chat__icon">🛒</div>
        <Typography.Title level={4} className="empty-chat__title">
          What are you shopping for?
        </Typography.Title>
        <Typography.Text type="secondary">Ask about any product on Amazon.</Typography.Text>
        <div className="empty-chat__examples">
          {EXAMPLES.map((text) => (
            <Button key={text} shape="round" disabled={disabled} onClick={() => onPick(text)}>
              {text}
            </Button>
          ))}
        </div>
      </div>
    </div>
  );
}
