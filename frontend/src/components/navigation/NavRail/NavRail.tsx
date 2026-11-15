import { BookOutlined, MessageOutlined } from "@ant-design/icons";
import { Tooltip } from "antd";
import type { ReactNode } from "react";
import "./NavRail.css";

export type Page = "threads" | "knowledge";

interface Props {
  page: Page;
  onNavigate: (page: Page) => void;
}

const ITEMS: { page: Page; label: string; icon: ReactNode }[] = [
  { page: "threads", label: "Threads", icon: <MessageOutlined /> },
  { page: "knowledge", label: "Knowledge base", icon: <BookOutlined /> },
];

// The app's pages, as a narrow icon bar on the far left
export function NavRail({ page, onNavigate }: Props) {
  return (
    <nav className="nav-rail" aria-label="Pages">
      <span className="nav-rail__brand" aria-hidden>
        🛒
      </span>
      {ITEMS.map((item) => (
        <Tooltip key={item.page} title={item.label} placement="right">
          <button
            type="button"
            className={`nav-rail__item${item.page === page ? " nav-rail__item--active" : ""}`}
            aria-label={item.label}
            aria-current={item.page === page ? "page" : undefined}
            onClick={() => onNavigate(item.page)}
          >
            {item.icon}
          </button>
        </Tooltip>
      ))}
    </nav>
  );
}
