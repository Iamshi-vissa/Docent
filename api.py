"""
api.py - FastAPI server wrapping the RAG engine (ingest, retriever, chat)
for consumption by Next.js React frontend.
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ingest import load_embedding_model, add_documents, IngestError
from retriever import retrieve_chunks
from chat import get_answer, ChatError, should_trigger_web_search
from web_search import perform_web_search

app = FastAPI(title="Docent RAG API")

# Enable CORS for Next.js frontend (localhost:3000 / localhost:3001)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global in-memory RAG state
STATE: Dict[str, Any] = {
    "chunks": [],
    "faiss_index": None,
    "documents": {},  # filename -> chunk_count
    "embedding_model": None,
}


def get_model():
    if STATE["embedding_model"] is None:
        STATE["embedding_model"] = load_embedding_model()
    return STATE["embedding_model"]


class QueryRequest(BaseModel):
    query: str
    conversation_history: Optional[List[Dict[str, Any]]] = None
    web_search_enabled: Optional[bool] = False
    active_document: Optional[str] = None


@app.get("/api/health")
def health():
    return {"status": "ok", "documents_count": len(STATE["documents"]), "total_chunks": len(STATE["chunks"])}


@app.get("/api/documents")
def get_documents():
    return {
        "documents": STATE["documents"],
        "total_chunks": len(STATE["chunks"])
    }


@app.post("/api/upload")
async def upload_documents(files: List[UploadFile] = File(...)):
    model = get_model()
    processed_count = 0
    errors = []

    for file in files:
        filename = file.filename or "uploaded_document"
        try:
            file_bytes = await file.read()
            merged_chunks, merged_index = add_documents(
                STATE["chunks"],
                STATE["faiss_index"],
                file_bytes,
                filename,
                model
            )
            added_chunks = len(merged_chunks) - len(STATE["chunks"])
            STATE["chunks"] = merged_chunks
            STATE["faiss_index"] = merged_index
            STATE["documents"][filename] = added_chunks
            processed_count += 1
        except IngestError as ie:
            errors.append(f"{filename}: {str(ie)}")
        except Exception as e:
            errors.append(f"{filename}: {str(e)}")

    return {
        "status": "success",
        "processed_files": processed_count,
        "documents": STATE["documents"],
        "total_chunks": len(STATE["chunks"]),
        "errors": errors
    }


@app.post("/api/query")
def query_rag(req: QueryRequest):
    retrieved = []
    if STATE["chunks"] and STATE["faiss_index"] is not None:
        model = get_model()
        retrieved = retrieve_chunks(
            req.query,
            STATE["faiss_index"],
            STATE["chunks"],
            model,
            top_k=4,
            filter_filename=req.active_document
        )


    web_chunks = []
    if should_trigger_web_search(req.query, manual_toggle=bool(req.web_search_enabled)):
        web_chunks = perform_web_search(req.query, max_results=4)

    if not retrieved and not web_chunks and not req.web_search_enabled:
        raise HTTPException(
            status_code=400,
            detail="No documents uploaded yet. Please upload a document or enable web search."
        )

    try:
        answer = get_answer(
            req.query,
            retrieved,
            conversation_history=req.conversation_history,
            web_chunks=web_chunks
        )
    except ChatError as ce:
        answer = f"⚠️ Error: {str(ce)}"

    return {
        "answer": answer,
        "retrieved_chunks": retrieved,
        "web_chunks": web_chunks
    }



@app.post("/api/reset")
def reset_rag():
    STATE["chunks"] = []
    STATE["faiss_index"] = None
    STATE["documents"] = {}
    return {"status": "reset", "message": "All documents and vector indexes cleared."}
