import { Layout as AntLayout } from "antd";
import { KnowledgePanel } from "../components/knowledge/KnowledgePanel/KnowledgePanel";

export function KnowledgePage() {
  return (
    <AntLayout.Content className="app__content">
      <KnowledgePanel />
    </AntLayout.Content>
  );
}
