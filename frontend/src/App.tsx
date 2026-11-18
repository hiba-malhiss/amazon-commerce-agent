import { Navigate, Route, Routes } from "react-router-dom";
import { ChatPage } from "./pages/ChatPage";
import { KnowledgePage } from "./pages/KnowledgePage";
import { Layout } from "./pages/Layout";
import "./App.css";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<ChatPage />} />
        <Route path="/chat/:threadId" element={<ChatPage />} />
        <Route path="/knowledge" element={<KnowledgePage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
