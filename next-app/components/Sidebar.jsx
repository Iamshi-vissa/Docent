"use client";

import React, { useState } from "react";
import { 
  Upload, 
  FileText, 
  Trash2, 
  Download, 
  AlertCircle, 
  Loader2, 
  BookOpen,
  PanelLeftClose
} from "lucide-react";

export default function Sidebar({ documents, setDocuments, onReset, messages, isOpen, onToggle, activeDocument, setActiveDocument }) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState(null);

  const handleFileUpload = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    setIsUploading(true);
    setUploadError(null);

    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const res = await fetch("http://localhost:8000/api/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Failed to upload document");
      }

      const data = await res.json();
      setDocuments(data.documents || {});
    } catch (err) {
      setUploadError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleDownloadChat = () => {
    if (!messages.length) return;
    const lines = [
      "# Docent Conversation Export",
      `_Exported: ${new Date().toLocaleString()}_\n`
    ];

    messages.forEach((m) => {
      const role = m.role === "user" ? "Q" : "A";
      lines.push(`**${role}:** ${m.content}\n`);
    });

    const blob = new Blob([lines.join("\n")], { type: "text/markdown" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `docent_chat_${Date.now()}.md`;
    a.click();
  };

  const docEntries = Object.entries(documents || {});

  if (!isOpen) return null;

  return (
    <aside className="w-80 h-screen sticky top-0 shrink-0 bg-[#121019]/95 border-r border-white/10 p-5 flex flex-col justify-between backdrop-blur-2xl z-20 text-slate-200 transition-all duration-300 overflow-y-auto">
      <div className="space-y-6">
        {/* Brand Title & Close Sidebar Toggle */}
        <div className="flex items-center justify-between pb-4 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-amber-500 to-rose-600 flex items-center justify-center text-white font-bold shadow-lg shadow-rose-950/40">
              <BookOpen className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-serif font-bold text-lg text-white leading-none">Docent RAG</h2>
              <span className="text-[11px] text-slate-400">Multi-Document AI Assistant</span>
            </div>
          </div>

          <button
            onClick={onToggle}
            className="p-1.5 rounded-xl bg-white/5 hover:bg-white/10 text-slate-400 hover:text-white transition border border-white/10"
            title="Close Sidebar"
          >
            <PanelLeftClose className="w-4 h-4" />
          </button>
        </div>

        {/* Upload Zone */}
        <div className="space-y-2">
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400">
            Upload Documents
          </label>
          <div className="relative group border-2 border-dashed border-white/15 hover:border-amber-500/50 rounded-2xl p-4 text-center bg-white/5 hover:bg-white/10 transition cursor-pointer">
            <input
              type="file"
              multiple
              accept=".pdf,.txt,.docx,.pptx"
              onChange={handleFileUpload}
              className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              disabled={isUploading}
            />
            {isUploading ? (
              <div className="flex flex-col items-center gap-2 py-2">
                <Loader2 className="w-6 h-6 text-amber-400 animate-spin" />
                <span className="text-xs text-slate-300 font-medium">Extracting & Indexing...</span>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-1.5 py-1">
                <Upload className="w-6 h-6 text-amber-400 group-hover:scale-110 transition-transform" />
                <span className="text-xs font-medium text-slate-200">Click or drag files here</span>
                <span className="text-[10px] text-slate-400">PDF, TXT, DOCX, PPTX</span>
              </div>
            )}
          </div>

          {uploadError && (
            <div className="flex items-center gap-1.5 text-xs text-rose-400 bg-rose-500/10 p-2.5 rounded-xl border border-rose-500/20">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{uploadError}</span>
            </div>
          )}
        </div>

        {/* Document List & Index Toggle */}
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-slate-400">
            <span>Document Index</span>
            <span className="text-amber-400 font-bold">{docEntries.length}</span>
          </div>

          {docEntries.length === 0 ? (
            <p className="text-xs text-slate-500 italic text-center py-4 bg-white/5 rounded-xl border border-white/5">
              No documents uploaded yet.
            </p>
          ) : (
            <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
              <button
                onClick={() => setActiveDocument && setActiveDocument(null)}
                className={`w-full flex items-center justify-between p-2.5 rounded-xl text-xs transition border ${
                  !activeDocument
                    ? "bg-amber-500/20 border-amber-500/50 text-amber-200 font-semibold"
                    : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10"
                }`}
              >
                <div className="flex items-center gap-2">
                  <BookOpen className="w-4 h-4 text-amber-400" />
                  <span>All Documents</span>
                </div>
                {!activeDocument && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded bg-amber-400/20 text-amber-300 font-bold">
                    Active
                  </span>
                )}
              </button>

              {docEntries.map(([name, count]) => {
                const isActive = activeDocument === name;
                return (
                  <button
                    key={name}
                    onClick={() => setActiveDocument && setActiveDocument(name)}
                    className={`w-full flex items-center justify-between p-2.5 rounded-xl text-xs transition border text-left ${
                      isActive
                        ? "bg-amber-500/20 border-amber-500/50 text-amber-200 font-semibold"
                        : "bg-white/5 border-white/10 text-slate-300 hover:bg-white/10"
                    }`}
                  >
                    <div className="flex items-center gap-2 overflow-hidden pr-2">
                      <FileText className="w-4 h-4 text-amber-400 shrink-0" />
                      <span className="truncate font-medium" title={name}>
                        {name}
                      </span>
                    </div>
                    <span className="text-[10px] px-2 py-0.5 rounded-md bg-amber-500/20 text-amber-300 font-semibold border border-amber-500/30 shrink-0">
                      {count} ch
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      </div>


      {/* Footer Controls */}
      <div className="space-y-2 pt-4 border-t border-white/10">
        {docEntries.length > 0 && (
          <button
            onClick={onReset}
            className="w-full py-2.5 px-3 rounded-xl bg-rose-500/15 hover:bg-rose-500/25 border border-rose-500/30 text-rose-300 text-xs font-semibold flex items-center justify-center gap-2 transition"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Reset Documents
          </button>
        )}

        {messages.length > 1 && (
          <button
            onClick={handleDownloadChat}
            className="w-full py-2.5 px-3 rounded-xl bg-white/10 hover:bg-white/15 border border-white/15 text-slate-200 text-xs font-semibold flex items-center justify-center gap-2 transition"
          >
            <Download className="w-3.5 h-3.5 text-amber-400" />
            Export Markdown
          </button>
        )}
      </div>
    </aside>
  );
}
