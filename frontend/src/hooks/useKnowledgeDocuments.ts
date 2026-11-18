import { useCallback, useEffect, useState } from "react";
import { deleteDocument, listDocuments, listKnowledgeBases, uploadDocument } from "../api/knowledgeBases";
import type { DocumentEvent, IndexingStep, KnowledgeBaseSummary, KnowledgeDocument } from "../api/types";
import { useDocumentEvents } from "./useDocumentEvents";

// Replace the document in the list, or add it on top when it's new
function upsert(documents: KnowledgeDocument[], document: KnowledgeDocument): KnowledgeDocument[] {
  const exists = documents.some((d) => d.id === document.id);
  return exists ? documents.map((d) => (d.id === document.id ? document : d)) : [document, ...documents];
}

// The knowledge bases, and the documents of the selected one. Status changes (indexing
// steps, ready, failed) arrive live from the server, including other tabs' uploads.
export function useKnowledgeDocuments() {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBaseSummary[]>([]);
  const [kbCode, setKbCode] = useState<string | null>(null);
  const [documents, setDocuments] = useState<KnowledgeDocument[]>([]);
  const [steps, setSteps] = useState<Record<string, IndexingStep>>({}); // by document id
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

  const applyEvent = useCallback(({ type, document, step }: DocumentEvent) => {
    setDocuments((prev) => (type === "deleted" ? prev.filter((d) => d.id !== document.id) : upsert(prev, document)));
    setSteps((prev) => {
      const { [document.id]: _previous, ...others } = prev;
      return step ? { ...others, [document.id]: step } : others;
    });
  }, []);

  const reload = useCallback(() => void refresh(), [refresh]);
  useDocumentEvents(kbCode, applyEvent, reload);

  // The responses update the list at once; the server's events confirm them
  const upload = useCallback(
    async (file: File) => {
      if (!kbCode) return;
      const document = await uploadDocument(kbCode, file);
      applyEvent({ type: "updated", document, step: null });
    },
    [kbCode, applyEvent],
  );

  const remove = useCallback(
    async (document: KnowledgeDocument) => {
      if (!kbCode) return;
      await deleteDocument(kbCode, document.id);
      applyEvent({ type: "deleted", document, step: null });
    },
    [kbCode, applyEvent],
  );

  return {
    knowledgeBases,
    kbCode,
    setKbCode,
    documents,
    steps,
    loading,
    error,
    upload,
    remove,
  };
}
