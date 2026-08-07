"use client";

import React, { useState } from "react";
import Sidebar from "@/components/Sidebar";
import AIQnAMenu from "@/components/AIQnAMenu";

export default function Page() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  const [documents, setDocuments] = useState({});
  const [messages, setMessages] = useState([
    {
      id: "1",
      role: "assistant",
      content: "Hello! I am Docent AI. Upload a document (PDF, TXT, DOCX, PPTX) in the sidebar to start asking questions grounded strictly in your content.",
      chunks: []
    }
  ]);

  const handleReset = async () => {
    try {
      await fetch("http://localhost:8000/api/reset", { method: "POST" });
    } catch (e) {
      console.error("Failed to reset backend state", e);
    }
    setDocuments({});
    setMessages([
      {
        id: Date.now().toString(),
        role: "assistant",
        content: "Reset complete. Upload a new document in the sidebar to begin.",
        chunks: []
      }
    ]);
  };

  return (
    <div className="flex min-h-screen w-full bg-[#0D0B12] overflow-hidden">
      <Sidebar
        documents={documents}
        setDocuments={setDocuments}
        onReset={handleReset}
        messages={messages}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(false)}
      />
      <main className="flex-1 flex flex-col min-w-0">
        <AIQnAMenu
          documents={documents}
          messages={messages}
          setMessages={setMessages}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={() => setIsSidebarOpen(true)}
        />
      </main>
    </div>
  );
}
