"""
app.py - Streamlit User Interface for Docent (Multi-Document RAG Assistant with Memory, Citations & Chat Export).
"""

import os
from io import BytesIO
from datetime import datetime, timezone
import streamlit as st
from dotenv import load_dotenv

# Load environment variables with override=True so edits to .env take effect immediately
load_dotenv(override=True)
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

# Import local pipeline modules & CSS theme generator
import importlib
import styles
import ingest
import chat
importlib.reload(styles)
importlib.reload(ingest)
importlib.reload(chat)

from ingest import load_embedding_model, process_multiple_documents
from retriever import retrieve_chunks
from chat import generate_answer
from styles import get_custom_css

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Docent - Multi-Document Q&A Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Initialize Session State ---
if "messages" not in st.session_state:
    st.session_state.messages = []

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None

if "stored_chunks" not in st.session_state:
    st.session_state.stored_chunks = None

if "current_file_names" not in st.session_state:
    st.session_state.current_file_names = []

if "doc_stats" not in st.session_state:
    st.session_state.doc_stats = {}

# --- Inject Claude.ai Warm Editorial CSS Block ONCE per Rerun ---
st.markdown(get_custom_css(), unsafe_allow_html=True)


# --- Dynamic Runtime Environment Diagnostics ---
groq_key = os.getenv("GROQ_API_KEY", "").strip()
xai_key = os.getenv("XAI_API_KEY", "").strip()

active_model = os.getenv("GROK_MODEL", "").strip() or os.getenv("GROQ_MODEL", "").strip() or "Not set"

if groq_key and groq_key != "your_groq_api_key_here":
    provider_label = "Groq"
    active_key_name = "GROQ_API_KEY"
    key_configured = True
elif xai_key and xai_key != "your_xai_api_key_here":
    provider_label = "xAI"
    active_key_name = "XAI_API_KEY"
    key_configured = True
else:
    provider_label = "API Key"
    active_key_name = "GROQ_API_KEY / XAI_API_KEY"
    key_configured = False


# --- Minimal Warm Sidebar Layout ---
with st.sidebar:
    st.markdown("### 📄 Docent")
    st.caption("Upload one or multiple documents to index.")
    
    # 1. Multi-Document File Uploader
    uploaded_files = st.file_uploader(
        "Select Document File(s)",
        type=["pdf", "txt", "docx", "pptx"],
        accept_multiple_files=True,
        help="200MB per file • PDF, TXT, DOCX, PPTX"
    )

    # 1c. Document List Display in Sidebar
    if st.session_state.doc_stats:
        st.divider()
        st.markdown(f"##### 📚 Loaded Documents ({len(st.session_state.doc_stats)})")
        for fname, count in st.session_state.doc_stats.items():
            st.caption(f"• **{fname}** (`{count}` chunks)")

    # 1d. Reset All Documents Button
    if st.session_state.stored_chunks:
        st.write("")
        if st.button("🗑️ Reset All Documents", use_container_width=True):
            st.session_state.faiss_index = None
            st.session_state.stored_chunks = None
            st.session_state.current_file_names = []
            st.session_state.doc_stats = {}
            st.session_state.messages = []
            st.rerun()

    # 4. Download Chat History Button (Rendered only if conversation exists)
    if st.session_state.messages:
        st.divider()
        export_lines = [
            "# Docent Chat History Export",
            f"Exported on: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"Active Documents: {', '.join(st.session_state.current_file_names) if st.session_state.current_file_names else 'None'}",
            "--------------------------------------------------\n"
        ]
        for msg in st.session_state.messages:
            role_label = "User Question" if msg["role"] == "user" else "Docent Assistant"
            export_lines.append(f"### 👤 {role_label}\n{msg['content']}\n")

        export_text = "\n".join(export_lines)
        st.download_button(
            label="📥 Download Chat",
            data=export_text,
            file_name=f"docent_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
            use_container_width=True
        )


# --- Cached Embedding Model Loading ---
@st.cache_resource(show_spinner="Loading local embedding model...")
def get_cached_embedding_model():
    """Cache the SentenceTransformer model in memory so it's loaded only once."""
    return load_embedding_model(EMBEDDING_MODEL_NAME)


try:
    embedding_model = get_cached_embedding_model()
except Exception as e:
    st.error(f"Failed to load sentence-transformers embedding model: {str(e)}")
    st.stop()


# --- Handle Multi-Document Upload & Ingestion ---
if uploaded_files:
    new_filenames = [f.name for f in uploaded_files]
    if sorted(st.session_state.current_file_names) != sorted(new_filenames):
        with st.spinner(f"Reading & indexing {len(uploaded_files)} document(s)..."):
            try:
                documents_tuples = [(BytesIO(f.read()), f.name) for f in uploaded_files]
                
                index, chunks = process_multiple_documents(
                    documents_list=documents_tuples,
                    embedding_model=embedding_model,
                    chunk_size=500,
                    chunk_overlap=50
                )

                # Calculate per-document chunk stats
                stats = {}
                for c in chunks:
                    s_file = c.get("source_file", "document")
                    stats[s_file] = stats.get(s_file, 0) + 1

                st.session_state.faiss_index = index
                st.session_state.stored_chunks = chunks
                st.session_state.current_file_names = new_filenames
                st.session_state.doc_stats = stats
                st.session_state.messages = []
                
                st.toast(f"Successfully indexed {len(uploaded_files)} document(s) ({len(chunks)} total chunks)", icon="🚀")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Error processing documents: {str(e)}")
                st.session_state.faiss_index = None
                st.session_state.stored_chunks = None
                st.session_state.current_file_names = []
                st.session_state.doc_stats = {}


# --- Main Header Section with Info Popover ---
col_head, col_popover = st.columns([0.84, 0.16])

with col_head:
    st.markdown('<div class="hero-accent-bar"></div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="app-header-title">Docent <span class="terracotta-dot">•</span></div>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<div class="app-header-subtitle">Ask questions, grounded in your documents</div>',
        unsafe_allow_html=True
    )

with col_popover:
    st.write("")
    with st.popover("ⓘ System Info", use_container_width=True, help="View System & Document Diagnostics"):
        st.markdown("##### ⚙️ System Diagnostics")
        st.markdown(f"• **LLM Model**: `{active_model}` ({provider_label})")
        st.markdown(f"• **Embedding Model**: `{EMBEDDING_MODEL_NAME}` (Local)")
        st.markdown(f"• **Vector Store**: `FAISS` In-Memory")
        if key_configured:
            st.markdown(f"• **API Key Status**: ✅ `{active_key_name}` Configured")
        else:
            st.markdown("• **API Key Status**: ❌ Missing API Key")

        st.divider()
        st.markdown("##### 📊 Document Statistics")
        if st.session_state.current_file_names and st.session_state.stored_chunks:
            st.markdown(f"• **Total Documents**: `{len(st.session_state.current_file_names)}`")
            st.markdown(f"• **Total Vector Chunks**: `{len(st.session_state.stored_chunks)}`")
            st.markdown("**Per-File Breakdown:**")
            for fname, count in st.session_state.doc_stats.items():
                st.markdown(f"  - `{fname}`: {count} chunks")
        else:
            st.markdown("*No documents uploaded yet*")


# --- Chat Interface Area ---
if st.session_state.faiss_index is None:
    # Empty State Hero Container
    st.markdown("""
    <div class="empty-state-card">
        <div class="empty-state-icon" style="font-size: 2.6rem; margin-bottom: 0.6rem;">📄🖋️</div>
        <div class="empty-state-title">Welcome to Docent</div>
        <div class="empty-state-desc">
            Upload one or multiple PDF, TXT, DOCX, or PPTX documents in the sidebar to build an in-memory vector index and start asking questions grounded directly in your files.
        </div>
        <div class="step-grid">
            <div class="step-card">
                <div class="step-num">1</div>
                <div class="step-title">Upload Documents</div>
                <div class="step-text">Choose one or multiple files in the sidebar.</div>
            </div>
            <div class="step-card">
                <div class="step-num">2</div>
                <div class="step-title">Merged Vector Store</div>
                <div class="step-text">All texts are chunked & merged into a single FAISS index.</div>
            </div>
            <div class="step-card">
                <div class="step-num">3</div>
                <div class="step-title">Cited Answers</div>
                <div class="step-text">Query with multi-turn memory & inline source citations.</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Render Conversation Messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Show context chunks expander for assistant messages if present
            if message["role"] == "assistant" and message.get("retrieved_chunks"):
                with st.expander("🔍 View Retrieved Context Chunks (Top 4)", expanded=False):
                    for i, chunk in enumerate(message["retrieved_chunks"], 1):
                        source_file = chunk.get("source_file") or chunk.get("filename") or "document"
                        score_percent = f"{chunk['score'] * 100:.1f}%"
                        st.markdown(f"""
                        <div class="chunk-card">
                            <div class="chunk-header" style="margin-bottom: 0.4rem; display: flex; gap: 8px; flex-wrap: wrap;">
                                <span class="badge-terracotta">📄 {source_file} (p.{chunk['page']})</span>
                                <span class="badge-sage">🎯 Score: {score_percent}</span>
                            </div>
                            <div class="chunk-snippet">{chunk['text']}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Chat Input Box
    if user_query := st.chat_input("Ask a question about your uploaded documents..."):
        # Display User Input
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        # Generate Assistant Answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking & synthesizing answer from retrieved context..."):
                # 1. Retrieve top 4 relevant chunks across ALL documents in FAISS index
                retrieved_chunks = retrieve_chunks(
                    query=user_query,
                    index=st.session_state.faiss_index,
                    chunks=st.session_state.stored_chunks,
                    model=embedding_model,
                    top_k=4
                )

                # 2. Call LLM API with inline citations and multi-turn conversation memory
                answer = generate_answer(
                    query=user_query,
                    retrieved_chunks=retrieved_chunks,
                    model_name=active_model,
                    conversation_history=st.session_state.messages[:-1]  # Exclude current question just appended
                )

                # 3. Display Generated Answer
                st.markdown(answer)

                # 4. Display Context Transparency Drawer
                if retrieved_chunks:
                    with st.expander("🔍 View Retrieved Context Chunks (Top 4)", expanded=False):
                        for i, chunk in enumerate(retrieved_chunks, 1):
                            source_file = chunk.get("source_file") or chunk.get("filename") or "document"
                            score_percent = f"{chunk['score'] * 100:.1f}%"
                            st.markdown(f"""
                            <div class="chunk-card">
                                <div class="chunk-header" style="margin-bottom: 0.4rem; display: flex; gap: 8px; flex-wrap: wrap;">
                                    <span class="badge-terracotta">📄 {source_file} (p.{chunk['page']})</span>
                                    <span class="badge-sage">🎯 Score: {score_percent}</span>
                                </div>
                                <div class="chunk-snippet">{chunk['text']}</div>
                            </div>
                            """, unsafe_allow_html=True)

            # 5. Save to Chat History
            st.session_state.messages.append({
                "role": "assistant",
                "content": answer,
                "retrieved_chunks": retrieved_chunks
            })
