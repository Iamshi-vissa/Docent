"use client";

import React, { useState, useEffect } from "react";
import Silk from "@/components/Silk";
import { 
  Send, 
  Sparkles, 
  BookOpen, 
  ChevronDown, 
  RefreshCw, 
  AlertCircle,
  FileText,
  Zap,
  ShieldCheck,
  Upload,
  ArrowRight
} from "lucide-react";

export default function AIQnAMenu({ documents, messages, setMessages }) {
  const [isMounted, setIsMounted] = useState(false);
  const [inputQuery, setInputQuery] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [expandedChunkId, setExpandedChunkId] = useState(null);
  const [apiError, setApiError] = useState(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const sampleQuestions = [
    "What are the main findings in the document?",
    "Summarize the key methodology and conclusions.",
    "What recommendations are highlighted in the report?"
  ];

  const handleSend = async (queryText) => {
    const q = queryText || inputQuery;
    if (!q.trim() || isGenerating) return;

    setApiError(null);
    const userMsg = { id: Date.now().toString(), role: "user", content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInputQuery("");
    setIsGenerating(true);

    try {
      const historyForLlm = messages
        .filter((m) => m.role === "user" || m.role === "assistant")
        .map((m) => ({ role: m.role, content: m.content }));

      const res = await fetch("http://localhost:8000/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: q,
          conversation_history: historyForLlm,
        }),
      });

      if (!res.ok) {
        const errData = await res.json();
        throw new Error(errData.detail || "Error communicating with RAG backend");
      }

      const data = await res.json();

      const assistantMsg = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.answer,
        chunks: data.retrieved_chunks || [],
      };

      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setApiError(err.message);
    } finally {
      setIsGenerating(false);
    }
  };

  const docCount = Object.keys(documents || {}).length;

  return (
    <div className="relative flex-1 flex flex-col min-h-screen overflow-hidden bg-[#0D0B12] text-slate-100 font-sans">
      {/* Background Studio - React Bits Silk Canvas */}
      <div 
        className="absolute inset-0 pointer-events-none z-0 opacity-40 overflow-hidden flex items-center justify-center"
        aria-hidden="true"
      >
        {isMounted && (
          <div style={{ width: '1080px', height: '1080px', position: 'relative' }}>
            <Silk
              speed={5}
              scale={1}
              color="#7B7481"
              noiseIntensity={1.5}
              rotation={0}
            />
          </div>
        )}
      </div>

      {/* Main Studio Overlay Container */}
      <div className="relative z-10 flex-1 flex flex-col max-w-5xl w-full mx-auto p-4 md:p-8">
        
        {/* Header */}
        <header className="flex items-center justify-between pb-4 mb-4 border-b border-white/10 backdrop-blur-md bg-white/5 rounded-2xl p-4 shadow-xl">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-amber-500 to-rose-600 flex items-center justify-center text-white font-bold shadow-lg shadow-rose-950/40">
              <Sparkles className="w-5 h-5" />
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
                AI Q&A Studio
                {docCount > 0 ? (
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-medium">
                    {docCount} File(s) Grounded
                  </span>
                ) : (
                  <span className="text-xs px-2.5 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-500/30 font-medium">
                    Ready for Ingestion
                  </span>
                )}
              </h1>
              <p className="text-xs text-slate-400">FAISS dense vector search + Groq LLM citation pipeline</p>
            </div>
          </div>

          {docCount > 0 && (
            <button 
              onClick={() => setMessages([messages[0]])}
              className="p-2 rounded-xl bg-white/5 hover:bg-white/10 text-slate-300 transition border border-white/10 text-xs flex items-center gap-1.5"
              title="Clear Chat Log"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Clear Chat</span>
            </button>
          )}
        </header>

        {/* API Error Notification */}
        {apiError && (
          <div className="mb-4 p-3 rounded-xl bg-rose-500/15 border border-rose-500/30 text-rose-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{apiError}</span>
          </div>
        )}

        {/* STATE A: BEFORE UPLOAD - Show Landing Features & Properties */}
        {docCount === 0 ? (
          <div className="flex-1 flex flex-col justify-center items-center my-auto py-8 px-4 text-center space-y-8 animate-fadeIn">
            
            {/* Hero Badge & Title */}
            <div className="space-y-3 max-w-2xl">
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs font-semibold">
                <Sparkles className="w-3.5 h-3.5" />
                <span>Multi-Document Retrieval Augmented Generation</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-serif font-bold text-white tracking-tight">
                Ask anything about your documents with exact source citations.
              </h2>
              <p className="text-slate-300 text-sm md:text-base leading-relaxed">
                Upload your files in the sidebar to build a local vector index. Docent retrieves relevant paragraphs and generates fact-grounded answers.
              </p>
            </div>

            {/* Feature Cards Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-4xl text-left">
              <div className="p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-amber-500/30 transition space-y-3 shadow-xl">
                <div className="w-10 h-10 rounded-xl bg-amber-500/20 text-amber-300 border border-amber-500/30 flex items-center justify-center">
                  <FileText className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-white text-base">Multi-Format Extraction</h3>
                <p className="text-xs text-slate-400 leading-normal">
                  Support for PDF, TXT, DOCX, and PPTX files. Automatically extracted page-by-page or slide-by-slide.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-rose-500/30 transition space-y-3 shadow-xl">
                <div className="w-10 h-10 rounded-xl bg-rose-500/20 text-rose-300 border border-rose-500/30 flex items-center justify-center">
                  <Zap className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-white text-base">Local FAISS Vectors</h3>
                <p className="text-xs text-slate-400 leading-normal">
                  384-dimensional dense semantic embeddings using SentenceTransformers for high-precision cosine search.
                </p>
              </div>

              <div className="p-5 rounded-2xl bg-white/5 border border-white/10 backdrop-blur-xl hover:border-emerald-500/30 transition space-y-3 shadow-xl">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 flex items-center justify-center">
                  <ShieldCheck className="w-5 h-5" />
                </div>
                <h3 className="font-semibold text-white text-base">Strict Grounding</h3>
                <p className="text-xs text-slate-400 leading-normal">
                  Zero hallucinations. Answers strictly reference <code className="text-emerald-300">[Source: file, page X]</code> citations.
                </p>
              </div>
            </div>

            {/* Quick Call to Action Banner */}
            <div className="p-4 rounded-2xl bg-gradient-to-r from-amber-500/10 to-rose-500/10 border border-white/15 backdrop-blur-2xl flex items-center gap-3 text-xs text-slate-200">
              <Upload className="w-5 h-5 text-amber-400 shrink-0" />
              <span>Select or drag files in the <strong>left sidebar</strong> to start querying your documents.</span>
            </div>

          </div>
        ) : (

          /* STATE B: AFTER UPLOAD - Show Chat Log & Interactive Query Input */
          <>
            {/* Chat Messages */}
            <div className="flex-1 overflow-y-auto space-y-6 pr-2 mb-4 scrollbar-thin scrollbar-thumb-white/10">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex flex-col ${
                    msg.role === "user" ? "items-end" : "items-start"
                  }`}
                >
                  <div
                    className={`max-w-3xl rounded-2xl p-5 shadow-2xl backdrop-blur-xl border ${
                      msg.role === "user"
                        ? "bg-rose-900/40 border-rose-500/30 text-rose-50 font-medium rounded-br-none"
                        : "bg-slate-900/70 border-white/10 text-slate-100 rounded-bl-none"
                    }`}
                  >
                    <div className="flex items-center gap-2 mb-2 text-xs font-semibold text-slate-400">
                      {msg.role === "user" ? (
                        <span className="text-rose-300 font-bold">You</span>
                      ) : (
                        <span className="text-amber-400 font-bold flex items-center gap-1">
                          <Sparkles className="w-3.5 h-3.5" /> Docent AI
                        </span>
                      )}
                    </div>

                    <div className="text-sm leading-relaxed whitespace-pre-wrap">
                      {msg.content}
                    </div>

                    {/* Sources & Citations Drawer */}
                    {msg.chunks && msg.chunks.length > 0 && (
                      <div className="mt-4 pt-3 border-t border-white/10">
                        <button
                          onClick={() =>
                            setExpandedChunkId(
                              expandedChunkId === msg.id ? null : msg.id
                            )
                          }
                          className="text-xs font-semibold text-amber-300 hover:text-amber-200 flex items-center gap-1.5 transition"
                        >
                          <BookOpen className="w-3.5 h-3.5" />
                          <span>Retrieved Context Sources ({msg.chunks.length})</span>
                          <ChevronDown
                            className={`w-3.5 h-3.5 transition-transform ${
                              expandedChunkId === msg.id ? "rotate-180" : ""
                            }`}
                          />
                        </button>

                        {expandedChunkId === msg.id && (
                          <div className="mt-3 space-y-2">
                            {msg.chunks.map((c, i) => (
                              <div
                                key={i}
                                className="p-3 rounded-xl bg-white/5 border border-white/10 text-xs space-y-1.5"
                              >
                                <div className="flex items-center justify-between">
                                  <span className="px-2 py-0.5 rounded-md bg-rose-500/20 text-rose-300 font-medium border border-rose-500/30">
                                    {c.filename || c.source_file} · p.{c.page}
                                  </span>
                                  <span className="px-2 py-0.5 rounded-md bg-emerald-500/20 text-emerald-300 font-medium border border-emerald-500/30">
                                    {((c.score || 0) * 100).toFixed(0)}% Relevance
                                  </span>
                                </div>
                                <p className="text-slate-300 italic">{c.text}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {isGenerating && (
                <div className="flex items-start">
                  <div className="rounded-2xl p-4 bg-slate-900/70 border border-white/10 text-slate-300 backdrop-blur-xl flex items-center gap-3 text-sm">
                    <Sparkles className="w-4 h-4 text-amber-400 animate-spin" />
                    <span>Searching vector index & generating response...</span>
                  </div>
                </div>
              )}
            </div>

            {/* Suggestion Chips */}
            {messages.length <= 2 && (
              <div className="flex flex-wrap gap-2 mb-4 justify-center">
                {sampleQuestions.map((sq, i) => (
                  <button
                    key={i}
                    onClick={() => handleSend(sq)}
                    className="text-xs px-3.5 py-2 rounded-xl bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 transition hover:border-amber-500/40 hover:text-white"
                  >
                    {sq}
                  </button>
                ))}
              </div>
            )}

            {/* Input Form Bar (Only rendered when docCount > 0) */}
            <div className="relative backdrop-blur-2xl bg-white/10 border border-white/15 rounded-2xl p-2 shadow-2xl">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleSend();
                }}
                className="flex items-center gap-2"
              >
                <input
                  type="text"
                  value={inputQuery}
                  onChange={(e) => setInputQuery(e.target.value)}
                  placeholder="Ask a question about your uploaded documents..."
                  disabled={!isMounted}
                  className="flex-1 bg-transparent border-none text-white placeholder-slate-400 px-4 py-3 text-sm focus:outline-none focus:ring-0"
                />
                <button
                  type="submit"
                  disabled={!isMounted || !inputQuery.trim() || isGenerating}
                  className="p-3 rounded-xl bg-gradient-to-r from-amber-500 to-rose-600 hover:from-amber-400 hover:to-rose-500 text-white disabled:opacity-40 disabled:cursor-not-allowed transition shadow-lg shadow-rose-950/40"
                >
                  <Send className="w-4 h-4" />
                </button>
              </form>
            </div>
          </>
        )}

      </div>
    </div>
  );
}
