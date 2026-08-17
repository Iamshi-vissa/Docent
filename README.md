# Docent

**A Multi-Document RAG Q&A Assistant & AI Studio**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Frontend](https://img.shields.io/badge/Frontend-Next.js%2016-black.svg)](https://nextjs.org/)
[![Vector Search](https://img.shields.io/badge/Vector%20Search-FAISS-4B8BBE.svg)](https://faiss.ai/)

---

## Overview

Docent is a production-ready, modular Retrieval-Augmented Generation (RAG) application. It accepts one or more documents (PDF, TXT, DOCX, PPTX) and answers questions grounded strictly in their content, with inline citations back to source files and page numbers.

Docent ships with two interchangeable interfaces:

- **Next.js AI Studio** — a modern React web interface with an interactive WebGL canvas background powered by React Bits Silk (`@react-bits/Silk-JS-TW`)
- **Streamlit App** — a single-file Python frontend for rapid local analysis

---

## Architecture & Pipeline

```
Upload (PDF / TXT / DOCX / PPTX)
        │
        ▼
Extract Text (pypdf / python-docx / python-pptx / plain decode)
        │
        ▼
Chunk Text (RecursiveCharacterTextSplitter — 500 chars, 50 overlap)
        │
        ▼
Embed Chunks (SentenceTransformers: all-MiniLM-L6-v2, runs 100% locally)
        │
        ▼
Index (FAISS, with pure-NumPy fallback — cosine similarity)
        │
        ▼
FastAPI RAG Backend / Streamlit App
        │
        ▼
Query → Vector Search → Retrieve Top-K Chunks → Construct Grounded Prompt
        │
        ▼
Groq Cloud API (Llama 3 / Mistral) → Grounded Answer with [Source: file, page] Citations
```

---

## Features

| Feature | Description |
|---|---|
| **Multi-format ingestion** | PDF, TXT, DOCX, and PPTX support with page-by-page or slide-by-slide metadata |
| **Local vector embeddings** | `all-MiniLM-L6-v2` runs locally to produce 384-dimensional dense vector embeddings |
| **FAISS vector search** | Cosine similarity matching, with automatic fallback to an in-memory NumPy index |
| **Grounded answers** | Prompt enforcement mandates answers rely solely on retrieved context, with explicit `[Source: filename, page X]` citations |
| **React Bits Silk Studio** | Next.js frontend with an animated WebGL canvas background (`speed=5`, `scale=1`, `color="#7B7481"`) |
| **FastAPI RAG engine** | REST endpoints (`/api/upload`, `/api/query`, `/api/documents`, `/api/reset`) connecting the Python RAG core to web clients |
| **Multi-turn memory & export** | Conversation history support with Markdown export |

---

## Project Structure

```
.
├── api.py              # FastAPI server exposing RAG REST API endpoints
├── app.py               # Streamlit web application frontend
├── ingest.py             # Multi-format text extraction, chunking, embedding, FAISS indexing
├── retriever.py           # Cosine similarity vector search against the FAISS index
├── chat.py               # Groq LLM client, citation system prompt, conversation history
├── styles.py              # Custom CSS design system for Streamlit
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
└── next-app/               # Next.js 16 + React Bits Silk Studio frontend
    ├── app/                # Next.js App Router (page.tsx, layout.tsx, globals.css)
    └── components/          # React components (Silk.jsx, Sidebar.jsx, AIQnAMenu.jsx)
```

---

## Getting Started

### 1. Environment Configuration

Copy `.env.example` to `.env` and set your Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
GROK_MODEL=llama-3.3-70b-versatile
```

A free API key is available at [console.groq.com](https://console.groq.com).

### 2. Option A — Next.js Studio App (Recommended)

**Terminal 1 — start the FastAPI RAG backend:**

```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

**Terminal 2 — start the Next.js frontend:**

```bash
cd next-app
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 3. Option B — Streamlit Standalone App

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## References

- Project repository: [github.com/Iamshi-vissa/Docent](https://github.com/Iamshi-vissa/Docent)
- P. Lewis et al., *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks,"* NeurIPS, 2020
- N. Reimers and I. Gurevych, *"Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks,"* EMNLP, 2019
- [Facebook AI Similarity Search (FAISS)](https://faiss.ai/)
- [sentence-transformers: all-MiniLM-L6-v2 model card](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)
- [pypdf documentation](https://pypdf.readthedocs.io/)
- [python-docx documentation](https://python-docx.readthedocs.io/)
- [LangChain text splitters documentation](https://python.langchain.com/)
- [Streamlit documentation](https://docs.streamlit.io/)
- [Groq API documentation](https://console.groq.com/docs)
- [DuckDuckGo Search (ddgs) documentation](https://pypi.org/project/ddgs/)
- [Next.js documentation](https://nextjs.org/docs)

---

## License

Distributed under the MIT License. Built for multi-document research and intelligent Q&A assistance.