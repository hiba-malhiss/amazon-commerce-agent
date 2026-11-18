import { Layout as AntLayout } from "antd";
import { useEffect, useRef } from "react";
import { Outlet, useLocation, useMatch, useNavigate } from "react-router-dom";
import { NavRail, type Page } from "../components/navigation/NavRail/NavRail";

// The app shell: the nav rail, with the active page rendered in the outlet.
export function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const knowledgeOpen = !!useMatch("/knowledge");

  // Remember the last chat location so the nav rail's "Threads" returns to it
  const lastChatPath = useRef("/");
  useEffect(() => {
    if (!knowledgeOpen) lastChatPath.current = location.pathname + location.search;
  }, [knowledgeOpen, location]);

  const goTo = (page: Page) => {
    navigate(page === "knowledge" ? "/knowledge" : lastChatPath.current);
  };

  return (
    <AntLayout hasSider className="app">
      <NavRail page={knowledgeOpen ? "knowledge" : "threads"} onNavigate={goTo} />
      <Outlet />
    </AntLayout>
  );
}
