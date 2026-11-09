"""
app.py - Docent: a multi-document RAG Q&A assistant.

Pipeline: upload (PDF/TXT/DOCX/PPTX) -> extract -> chunk -> embed locally
-> FAISS retrieval -> Groq LLM generation with citations and conversation memory.
"""

import os
import re
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from ingest import load_embedding_model, add_documents, SUPPORTED_EXTENSIONS, IngestError, EMBEDDING_MODEL_NAME
from retriever import retrieve_chunks
from chat import get_answer, ChatError, DEFAULT_MODEL, should_trigger_web_search
from web_search import perform_web_search
from styles import get_custom_css

load_dotenv()

st.set_page_config(
    page_title="Docent",
    page_icon="D",
    layout="wide",
)

st.markdown(get_custom_css(), unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Session state initialization
# ---------------------------------------------------------------------------

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None
if "chunks" not in st.session_state:
    st.session_state.chunks = []
if "documents" not in st.session_state:
    st.session_state.documents = {}  # filename -> chunk count
if "messages" not in st.session_state:
    st.session_state.messages = []  # {"role", "content"} for display + LLM history
if "processed_filenames" not in st.session_state:
    st.session_state.processed_filenames = set()
if "web_search_enabled" not in st.session_state:
    st.session_state.web_search_enabled = False
if "active_document" not in st.session_state:
    st.session_state.active_document = None


@st.cache_resource(show_spinner=False)
def get_embedding_model():
    return load_embedding_model()


# ---------------------------------------------------------------------------
# Sidebar: upload + document list + reset + download + web search toggle
# ---------------------------------------------------------------------------

with st.sidebar:
    st.markdown('<div class="sidebar-heading">Settings & Search</div>', unsafe_allow_html=True)
    st.session_state.web_search_enabled = st.checkbox(
        "🌐 Search Internet Sites",
        value=st.session_state.web_search_enabled,
        help="Search external internet websites and append site citations at the end of answers.",
    )

    st.markdown('<div class="sidebar-heading" style="margin-top: 1rem;">Document Index (Click to Toggle Focus)</div>', unsafe_allow_html=True)

    uploaded_files = st.file_uploader(
        "Select document file(s)",
        type=SUPPORTED_EXTENSIONS,
        accept_multiple_files=True,
        help="PDF, TXT, or DOCX — 200MB max per file.",
        label_visibility="collapsed",
    )

    if uploaded_files:
        model = get_embedding_model()
        new_files = [f for f in uploaded_files if f.name not in st.session_state.processed_filenames]

        if new_files:
            with st.spinner(f"Reading {len(new_files)} document(s)..."):
                for f in new_files:
                    try:
                        file_bytes = f.getvalue()
                        merged_chunks, merged_index = add_documents(
                            st.session_state.chunks,
                            st.session_state.faiss_index,
                            file_bytes,
                            f.name,
                            model,
                        )
                        chunk_count = len(merged_chunks) - len(st.session_state.chunks)
                        st.session_state.chunks = merged_chunks
                        st.session_state.faiss_index = merged_index
                        st.session_state.documents[f.name] = chunk_count
                        st.session_state.processed_filenames.add(f.name)
                    except IngestError as e:
                        st.error(str(e))

    if st.session_state.documents:
        doc_options = ["📁 All Documents"] + [f"📄 {fname}" for fname in st.session_state.documents.keys()]

        # Calculate current radio selection index
        current_index = 0
        if st.session_state.active_document and st.session_state.active_document in st.session_state.documents:
            current_index = list(st.session_state.documents.keys()).index(st.session_state.active_document) + 1

        selected_doc = st.radio(
            "Active Context Focus",
            options=doc_options,
            index=current_index,
            label_visibility="collapsed",
            key="document_focus_radio"
        )

        if selected_doc == "📁 All Documents":
            st.session_state.active_document = None
        else:
            st.session_state.active_document = selected_doc.replace("📄 ", "")

        st.markdown("&nbsp;", unsafe_allow_html=True)
        if st.button("Reset documents", use_container_width=True):
            st.session_state.faiss_index = None
            st.session_state.chunks = []
            st.session_state.documents = {}
            st.session_state.processed_filenames = set()
            st.session_state.messages = []
            st.session_state.active_document = None
            st.rerun()


    # Download chat history
    if st.session_state.messages:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        lines = ["# Docent conversation export", f"_Exported {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n"]
        for m in st.session_state.messages:
            role = "Q" if m["role"] == "user" else "A"
            lines.append(f"**{role}:** {m['content']}\n")
        export_text = "\n".join(lines)

        st.download_button(
            "Download chat",
            data=export_text,
            file_name=f"docent_chat_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
            mime="text/markdown",
            use_container_width=True,
        )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------

header_col, info_col = st.columns([6, 1])

with header_col:
    st.markdown(
        """<div class="docent-header">
            <div class="docent-title">Docent</div>
            <div class="docent-accent-bar"></div>
            <div class="docent-tagline">Ask questions, grounded in your documents and the web.</div>
        </div>""",
        unsafe_allow_html=True,
    )

with info_col:
    st.markdown("<div style='padding-top: 1.2rem;'></div>", unsafe_allow_html=True)
    with st.popover("Info"):
        api_key_set = bool(os.getenv("GROQ_API_KEY"))
        model_name = os.getenv("GROK_MODEL", DEFAULT_MODEL)

        st.markdown("**Pipeline**")
        st.caption("Documents are chunked, embedded locally, retrieved via FAISS, and combined with optional web search results to answer queries.")
        st.markdown("---")
        st.markdown(f"**Embedding model:** `{EMBEDDING_MODEL_NAME}` (local)")
        st.markdown(f"**LLM model:** `{model_name}` (Groq)")
        st.markdown("**Vector store:** FAISS (in-memory)")
        st.markdown(f"**Internet Search:** {'Enabled' if st.session_state.web_search_enabled else 'Disabled'}")
        st.markdown(f"**API key:** {'Active' if api_key_set else 'Not set'}")

        if st.session_state.documents:
            st.markdown("---")
            st.markdown("**Loaded documents**")
            for fname, count in st.session_state.documents.items():
                st.caption(f"{fname} — {count} chunks")
        else:
            st.markdown("---")
            st.caption("No document uploaded yet.")


# ---------------------------------------------------------------------------
# Main chat area
# ---------------------------------------------------------------------------

def render_citations(text: str) -> str:
    """Wraps [Source: ...] tags in a styled span for display."""
    pattern = r"(\[Source:[^\]]+\])"
    return re.sub(pattern, r'<span class="citation-tag">\1</span>', text)


if not st.session_state.documents and not st.session_state.web_search_enabled:
    st.markdown(
        """<div class="empty-state-card">
            <div class="empty-state-title">Upload a document or enable Internet Search to begin</div>
            <div class="empty-state-desc">
                Add PDF, TXT, or DOCX files in the sidebar, or enable <b>🌐 Search Internet Sites</b> to query live web sources.
            </div>
        </div>""",
        unsafe_allow_html=True,
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """<div class="step-card"><div class="step-num">1</div>
            <div class="step-title">Upload / Search</div>
            <div class="step-text">Add document files or check Internet Search in the sidebar.</div>
            </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(
            """<div class="step-card"><div class="step-num">2</div>
            <div class="step-title">Index / Retrieve</div>
            <div class="step-text">Documents are indexed locally; web queries fetch live sources.</div>
            </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(
            """<div class="step-card"><div class="step-num">3</div>
            <div class="step-title">Ask</div>
            <div class="step-text">Get answers with clean formatting and site citations.</div>
            </div>""", unsafe_allow_html=True)

else:
    # Render existing conversation
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(render_citations(msg["content"]), unsafe_allow_html=True)
            if msg["role"] == "assistant":
                if msg.get("chunks"):
                    with st.expander(f"Document Sources ({len(msg['chunks'])})"):
                        for c in msg["chunks"]:
                            st.markdown(
                                f"""<div class="chunk-card">
                                    <div class="chunk-meta">
                                        <span class="chunk-badge page">{c['filename']} · p.{c['page']}</span>
                                        <span class="chunk-badge score">{c['score']*100:.0f}% relevance</span>
                                    </div>
                                    {c['text'][:400]}{'...' if len(c['text']) > 400 else ''}
                                </div>""",
                                unsafe_allow_html=True,
                            )
                if msg.get("web_chunks"):
                    with st.expander(f"Internet Sources ({len(msg['web_chunks'])})"):
                        for w in msg["web_chunks"]:
                            st.markdown(
                                f"- **[{w.get('title', 'Web Page')}]({w.get('url', '#')})**\n  _{w.get('snippet', '')}_"
                            )

    placeholder_text = "Ask a question..." if st.session_state.web_search_enabled else "Ask a question about your uploaded documents..."
    question = st.chat_input(placeholder_text)

    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                retrieved = []
                if st.session_state.documents and st.session_state.faiss_index:
                    model = get_embedding_model()
                    retrieved = retrieve_chunks(
                        question,
                        st.session_state.faiss_index,
                        st.session_state.chunks,
                        model,
                        top_k=4,
                        filter_filename=st.session_state.active_document
                    )

                web_chunks = []
                if should_trigger_web_search(question, manual_toggle=st.session_state.web_search_enabled):
                    web_chunks = perform_web_search(question, max_results=4)

                history_for_llm = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages[:-1]  # exclude current question, added separately
                ]

                try:
                    answer = get_answer(
                        question,
                        retrieved,
                        conversation_history=history_for_llm,
                        web_chunks=web_chunks
                    )
                except ChatError as e:
                    answer = f"{e}"

            st.markdown(render_citations(answer), unsafe_allow_html=True)

            if retrieved:
                with st.expander(f"Document Sources ({len(retrieved)})"):
                    for c in retrieved:
                        st.markdown(
                            f"""<div class="chunk-card">
                                <div class="chunk-meta">
                                    <span class="chunk-badge page">{c['filename']} · p.{c['page']}</span>
                                    <span class="chunk-badge score">{c['score']*100:.0f}% relevance</span>
                                </div>
                                {c['text'][:400]}{'...' if len(c['text']) > 400 else ''}
                            </div>""",
                            unsafe_allow_html=True,
                        )

            if web_chunks:
                with st.expander(f"Internet Sources ({len(web_chunks)})"):
                    for w in web_chunks:
                        st.markdown(
                            f"- **[{w.get('title', 'Web Page')}]({w.get('url', '#')})**\n  _{w.get('snippet', '')}_"
                        )

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "chunks": retrieved,
            "web_chunks": web_chunks
        })

