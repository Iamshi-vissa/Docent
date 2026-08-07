# Docent — Multi-Document RAG Q&A Assistant & AI Studio

**Docent** is a production-ready, modular **Retrieval-Augmented Generation (RAG)** application. It lets you upload one or more documents (**PDF, TXT, DOCX, PPTX**) and interactively ask questions with answers strictly grounded in your content, featuring inline citations back to source files and page numbers.

Docent provides two seamless interfaces:
1. **Next.js AI Studio**: A modern React web interface featuring an interactive canvas background powered by **React Bits Silk Canvas** (`@react-bits/Silk-JS-TW`).
2. **Streamlit App**: A single-file desktop/web Python frontend for rapid local analysis.

---

## 🏗 Architecture & Pipeline

```
Upload (PDF / TXT / DOCX / PPTX)
    │
    ▼
Extract Text (pypdf / python-docx / python-pptx / plain decode)
    │
    ▼
Chunk Text (RecursiveCharacterTextSplitter: 500 chars, 50 overlap)
    │
    ▼
Embed Chunks (SentenceTransformers: all-MiniLM-L6-v2, runs 100% locally)
    │
    ▼
Index (FAISS / pure-NumPy fallback vector store, Cosine Similarity)
    │
    ▼
FastAPI RAG Backend / Streamlit App
    │
    ▼
Query Vector Search -> Retrieve Top-K Chunks -> Construct Grounded Prompt
    │
    ▼
Groq Cloud API (Llama 3 / Mistral) -> Grounded Answer with [Source: file, page] Citations
```

---

## ✨ Features

- **Multi-Format Ingestion**: PDF, TXT, DOCX, and PPTX support with page-by-page or slide-by-slide metadata.
- **Local Vector Embeddings**: Utilizes `all-MiniLM-L6-v2` locally for fast 384-dimensional dense vector embeddings.
- **FAISS Vector Search**: Instant cosine similarity matching with fallback to in-memory NumPy vector indexing.
- **Zero Hallucinations**: Prompt enforcement mandates answers rely solely on context excerpts with explicit `[Source: filename, page X]` citations.
- **React Bits Silk Studio**: Next.js frontend with an animated WebGL `Silk` studio canvas background (`speed={5}`, `scale={1}`, `color="#7B7481"`).
- **FastAPI RAG Engine**: REST API endpoints (`/api/upload`, `/api/query`, `/api/documents`, `/api/reset`) connecting Python RAG with web clients.
- **Multi-Turn Memory & Export**: Conversation memory support and Markdown export functionality.

---

## 📂 Project Structure

```
.
├── api.py              # FastAPI server exposing RAG REST API endpoints
├── app.py              # Streamlit web application frontend
├── ingest.py           # Multi-format text extraction, chunking, embedding, FAISS indexing
├── retriever.py        # Cosine similarity vector search against FAISS index
├── chat.py             # Groq LLM client, citation system prompt, conversation history
├── styles.py           # Custom CSS design system for Streamlit
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
└── next-app/           # Next.js 16 + React Bits Silk Studio frontend
    ├── app/            # Next.js App Router (page.tsx, layout.tsx, globals.css)
    └── components/     # React Components (Silk.jsx, Sidebar.jsx, AIQnAMenu.jsx)
```

---

## 🚀 Setup & Execution

### 1. Environment Configuration

Copy `.env.example` to `.env` and set your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
GROK_MODEL=llama-3.3-70b-versatile
```

*(Get a free API key at [console.groq.com](https://console.groq.com))*

---

### 2. Option A: Run Next.js Studio App (Recommended)

#### Start FastAPI RAG Backend (Terminal 1)
```powershell
.\venv\Scripts\Activate.ps1
python -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
```

#### Start Next.js React Bits Silk Frontend (Terminal 2)
```powershell
cd next-app
npm run dev
```

Open **[http://localhost:3000](http://localhost:3000)** in your browser.

---

### 3. Option B: Run Streamlit Standalone App

```powershell
.\venv\Scripts\Activate.ps1
streamlit run app.py
```

Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 📜 License

MIT License. Built for multi-document research and intelligent Q&A assistance.