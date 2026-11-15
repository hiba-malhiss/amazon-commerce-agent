import { DeleteOutlined, EyeOutlined, FileTextOutlined, LoadingOutlined, UploadOutlined } from "@ant-design/icons";
import { App as AntApp, Alert, Button, Popconfirm, Select, Table, Tag, Tooltip, Typography, Upload } from "antd";
import type { ColumnsType } from "antd/es/table";
import { useState } from "react";
import type { DocumentStatus, KnowledgeDocument } from "../../../api/types";
import { KNOWLEDGE_FILE_TYPES, MAX_UPLOAD_MB } from "../../../config";
import { useKnowledgeDocuments } from "../../../hooks/useKnowledgeDocuments";
import { ChunksDrawer } from "../ChunksDrawer/ChunksDrawer";
import "./KnowledgePanel.css";

const STATUS_TAG: Record<DocumentStatus, { color: string; label: string }> = {
  indexing: { color: "processing", label: "Indexing" },
  ready: { color: "success", label: "Ready" },
  failed: { color: "error", label: "Failed" },
};

// Upload, list, review the chunks of, and delete the documents the agent answers policy questions from
export function KnowledgePanel() {
  const { message } = AntApp.useApp();
  const { knowledgeBases, kbCode, setKbCode, documents, loading, error, upload, remove } = useKnowledgeDocuments();
  const [reviewedDocument, setReviewedDocument] = useState<KnowledgeDocument | null>(null);

  const handleUpload = async (file: File) => {
    const tooLarge = file.size > MAX_UPLOAD_MB * 1024 * 1024;
    if (tooLarge) {
      message.error(`${file.name} is larger than ${MAX_UPLOAD_MB} MB`);
      return;
    }
    try {
      await upload(file);
      message.success(`${file.name} uploaded, indexing in the background`);
    } catch (e) {
      message.error(`Couldn't upload ${file.name}: ${(e as Error).message}`);
    }
  };

  const handleDelete = async (document: KnowledgeDocument) => {
    try {
      await remove(document.id);
      message.success(`${document.filename} deleted`);
    } catch (e) {
      message.error(`Couldn't delete ${document.filename}: ${(e as Error).message}`);
    }
  };

  const columns: ColumnsType<KnowledgeDocument> = [
    {
      title: "File",
      dataIndex: "filename",
      render: (filename: string) => (
        <span className="knowledge__file">
          <FileTextOutlined /> {filename}
        </span>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      width: 130,
      render: (status: DocumentStatus, document) => {
        const tag = (
          <Tag color={STATUS_TAG[status].color} icon={status === "indexing" ? <LoadingOutlined /> : undefined}>
            {STATUS_TAG[status].label}
          </Tag>
        );
        return document.error ? <Tooltip title={document.error}>{tag}</Tooltip> : tag;
      },
    },
    { title: "Chunks", dataIndex: "chunk_count", width: 90 },
    {
      title: "Updated",
      dataIndex: "updated_at",
      width: 190,
      render: (value: string) => new Date(value).toLocaleString(),
    },
    {
      key: "actions",
      width: 100,
      render: (_, document) => (
        <span className="knowledge__row-actions">
          <Tooltip title={document.status === "ready" ? "View chunks" : "Available once indexed"}>
            <Button
              type="text"
              icon={<EyeOutlined />}
              disabled={document.status !== "ready"}
              aria-label={`View the chunks of ${document.filename}`}
              onClick={() => setReviewedDocument(document)}
            />
          </Tooltip>
          <Popconfirm
            title={`Delete ${document.filename}?`}
            description="The agent will stop using it."
            okText="Delete"
            okButtonProps={{ danger: true }}
            onConfirm={() => handleDelete(document)}
          >
            <Button type="text" danger icon={<DeleteOutlined />} aria-label={`Delete ${document.filename}`} />
          </Popconfirm>
        </span>
      ),
    },
  ];

  return (
    <div className="knowledge">
      <div className="knowledge__header">
        <div>
          <Typography.Title level={4} className="knowledge__title">
            Knowledge base
          </Typography.Title>
          <Typography.Text type="secondary">
            Documents the agent answers policy questions from ({KNOWLEDGE_FILE_TYPES.join(", ")}, up to {MAX_UPLOAD_MB}{" "}
            MB)
          </Typography.Text>
        </div>
        <div className="knowledge__actions">
          {knowledgeBases.length > 1 && (
            <Select
              value={kbCode}
              onChange={setKbCode}
              options={knowledgeBases.map((kb) => ({
                value: kb.code,
                label: kb.name,
              }))}
              className="knowledge__select"
            />
          )}
          <Upload
            accept={KNOWLEDGE_FILE_TYPES.join(",")}
            multiple
            showUploadList={false}
            disabled={!kbCode}
            beforeUpload={(file) => {
              void handleUpload(file);
              return false; // handled above, not by the Upload component
            }}
          >
            <Button type="primary" icon={<UploadOutlined />} disabled={!kbCode}>
              Upload files
            </Button>
          </Upload>
        </div>
      </div>

      {error && <Alert type="error" showIcon message={error} className="knowledge__error" />}

      <Table
        rowKey="id"
        columns={columns}
        dataSource={documents}
        loading={loading}
        pagination={false}
        locale={{
          emptyText: "No documents yet: upload a PDF, TXT, or Markdown file",
        }}
      />

      {kbCode && <ChunksDrawer kbCode={kbCode} document={reviewedDocument} onClose={() => setReviewedDocument(null)} />}
    </div>
  );
}
