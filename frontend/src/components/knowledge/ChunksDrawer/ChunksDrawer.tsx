import { Alert, Drawer, Empty, Spin, Tag, Typography } from "antd";
import { useEffect, useState } from "react";
import { listChunks } from "../../../api/knowledgeBases";
import type { KnowledgeChunk, KnowledgeDocument } from "../../../api/types";
import "./ChunksDrawer.css";

interface Props {
  kbCode: string;
  document: KnowledgeDocument | null; // null = closed
  onClose: () => void;
}

export function ChunksDrawer({ kbCode, document, onClose }: Props) {
  const [chunks, setChunks] = useState<KnowledgeChunk[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!document) return;
    let cancelled = false; // a newer document was opened before this one loaded
    setLoading(true);
    setError(null);
    listChunks(kbCode, document.id)
      .then((list) => !cancelled && setChunks(list))
      .catch((e: Error) => !cancelled && setError(e.message))
      .finally(() => !cancelled && setLoading(false));
    return () => {
      cancelled = true;
    };
  }, [kbCode, document]);

  return (
    <Drawer
      open={document !== null}
      onClose={onClose}
      size="large"
      title={document?.filename}
      extra={document && <Typography.Text type="secondary">{document.chunk_count} chunks</Typography.Text>}
      destroyOnHidden
    >
      {error && <Alert type="error" showIcon message={error} />}
      {loading ? (
        <Spin className="chunks__loading" />
      ) : chunks.length === 0 && !error ? (
        <Empty description="No chunks: the document isn't indexed yet" />
      ) : (
        <ol className="chunks">
          {chunks.map((chunk) => (
            <li key={chunk.id} className="chunk">
              <div className="chunk__meta">
                <Tag>#{chunk.chunk_index + 1}</Tag>
                <span className="chunk__section">{chunk.section_path ?? "No heading"}</span>
                {chunk.page_start !== null && (
                  <Tag>
                    {chunk.page_start === chunk.page_end
                      ? `page ${chunk.page_start}`
                      : `pages ${chunk.page_start}–${chunk.page_end}`}
                  </Tag>
                )}
                <span className="chunk__tokens">{chunk.token_count} tokens</span>
              </div>
              <pre className="chunk__content">{chunk.content}</pre>
            </li>
          ))}
        </ol>
      )}
    </Drawer>
  );
}
