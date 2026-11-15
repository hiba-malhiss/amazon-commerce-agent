import { useCallback, useEffect, useState } from "react";
import { deleteDocument, listDocuments, listKnowledgeBases, uploadDocument } from "../api/knowledgeBases";
import type { KnowledgeBaseSummary, KnowledgeDocument } from "../api/types";
import { KNOWLEDGE_POLL_MS } from "../config";

// The knowledge bases, and the documents of the selected one. Refreshes on its own while
// any document is still indexing; unmounting stops it.
export function useKnowledgeDocuments() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseSummary[]>([]);
  const [kbCode, setKbCode] = useState<string | null>(null);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (knowledgeBases.length > 0) return;
    listKnowledgeBases()
      .then((list) => {
        setKnowledgeBases(list);
        setKbCode((code) => code ?? list[0]?.code ?? null);
      })
      .catch((e: Error) => setError(e.message));
  }, [knowledgeBases.length]);

  const refresh = useCallback(async () => {
    if (!kbCode) return;
    try {
      setDocuments(await listDocuments(kbCode));
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    }
  }, [kbCode]);

  useEffect(() => {
    if (!kbCode) return;
    setLoading(true);
    void refresh().finally(() => setLoading(false));
  }, [kbCode, refresh]);

  // Poll while something is indexing, so its status turns ready / failed by itself
  const indexing = documents.some((d) => d.status === "indexing");
  useEffect(() => {
    if (!indexing) return;
    const timer = window.setInterval(() => void refresh(), KNOWLEDGE_POLL_MS);
    return () => window.clearInterval(timer);
  }, [indexing, refresh]);

  const upload = useCallback(
    async (file: File) => {
      if (!kbCode) return;
      await uploadDocument(kbCode, file);
      await refresh();
    },
    [kbCode, refresh],
  );

  const remove = useCallback(
    async (documentId: string) => {
      if (!kbCode) return;
      await deleteDocument(kbCode, documentId);
      await refresh();
    },
    [kbCode, refresh],
  );

  return {
    knowledgeBases,
    kbCode,
    setKbCode,
    documents,
    loading,
    error,
    upload,
    remove,
  };
}
