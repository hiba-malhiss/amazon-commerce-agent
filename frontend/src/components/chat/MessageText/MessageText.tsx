import { Typography } from "antd";
import Markdown from "react-markdown";
import remarkGfm from "remark-gfm";
import "./MessageText.css";

interface Props {
  text: string;
  markdown: boolean;
}

export function MessageText({ text, markdown }: Props) {
  if (!markdown) {
    return <Typography.Paragraph className="bubble__text">{text}</Typography.Paragraph>;
  }
  return (
    <div className="bubble__text bubble__md">
      <Markdown
        remarkPlugins={[remarkGfm]}
        components={{
          a: ({ href, children }) => (
            <a href={href} target="_blank" rel="noopener noreferrer">
              {children}
            </a>
          ),
        }}
      >
        {text}
      </Markdown>
    </div>
  );
}
