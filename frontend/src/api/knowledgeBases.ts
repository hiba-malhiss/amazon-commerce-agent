import { request } from "./http";
import type {
  KnowledgeBaseSummary,
  KnowledgeChunk,
  KnowledgeChunkListResponse,
  KnowledgeDocument,
  KnowledgeDocumentListResponse,
} from "./types";

export function listKnowledgeBases(): Promise<KnowledgeBaseSummary[]> {
  return request<KnowledgeBaseSummary[]>("/knowledge-bases");
}

export async function listDocuments(kbCode: string): Promise<KnowledgeDocument[]> {
  const { documents } = await request<KnowledgeDocumentListResponse>(`/knowledge-bases/${kbCode}/documents`);
  return documents;
}

// The document comes back "indexing" (or "ready" when the same content is already indexed)
export function uploadDocument(kbCode: string, file: File): Promise<KnowledgeDocument> {
  const body = new FormData();
  body.append("file", file);
  return request<KnowledgeDocument>(`/knowledge-bases/${kbCode}/documents`, {
    method: "POST",
    body,
  });
}

export function deleteDocument(kbCode: string, documentId: string): Promise<void> {
  return request<void>(`/knowledge-bases/${kbCode}/documents/${documentId}`, {
    method: "DELETE",
  });
}

// A document's chunks in order, as they were indexed (empty until it's ready)
export async function listChunks(kbCode: string, documentId: string): Promise<KnowledgeChunk[]> {
  const { chunks } = await request<KnowledgeChunkListResponse>(
    `/knowledge-bases/${kbCode}/documents/${documentId}/chunks`,
  );
  return chunks;
}

// WebSocket path that pushes every document change of the knowledge base (DocumentEvent)
export function documentEventsPath(kbCode: string): string {
  return `/knowledge-bases/${kbCode}/documents/events`;
}
