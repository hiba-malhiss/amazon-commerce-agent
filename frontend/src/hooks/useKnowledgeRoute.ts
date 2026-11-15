import { useCallback, useEffect, useState } from "react";

// The knowledge base page lives at /knowledge; chats keep /chat/<id> (useUrlThreadId)
const KNOWLEDGE_PATH = "/knowledge";

function isKnowledgePath(): boolean {
  return window.location.pathname === KNOWLEDGE_PATH;
}

export function useKnowledgeRoute() {
  const [knowledgeOpen, setKnowledgeOpen] = useState(isKnowledgePath);

  useEffect(() => {
    // Back / forward between a chat and the knowledge page
    const onPop = () => setKnowledgeOpen(isKnowledgePath());
    window.addEventListener("popstate", onPop);
    return () => window.removeEventListener("popstate", onPop);
  }, []);

  const openKnowledge = useCallback(() => {
    if (!isKnowledgePath()) window.history.pushState(null, "", KNOWLEDGE_PATH);
    setKnowledgeOpen(true);
  }, []);

  // Opening a chat changes the URL itself (useUrlThreadId); this only hides the page
  const closeKnowledge = useCallback(() => setKnowledgeOpen(false), []);

  return { knowledgeOpen, openKnowledge, closeKnowledge };
}
