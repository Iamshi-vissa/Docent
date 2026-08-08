"""
retriever.py - Vector Similarity Search using FAISS and SentenceTransformer embeddings.
"""

from typing import List, Dict, Any, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


def retrieve_chunks(
    query: str,
    index: faiss.IndexFlatIP,
    chunks: List[Dict[str, Any]],
    model: SentenceTransformer,
    top_k: int = 4,
    filter_filename: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Embeds the user query, searches the FAISS index for top_k similar vectors,
    and returns matching chunk dictionaries with similarity scores.
    Optionally filters chunks by a specific filename if filter_filename is set.
    
    Args:
        query: User input question string.
        index: Trained FAISS IndexFlatIP.
        chunks: List of chunk metadata dicts corresponding to FAISS vector indices.
        model: SentenceTransformer embedding model.
        top_k: Number of top chunks to retrieve (default: 4).
        filter_filename: Optional filename to filter chunks for single-document focus.
        
    Returns:
        List of dicts: [{'text': ..., 'page': ..., 'score': float, 'id': int}, ...]
    """
    if not query or not query.strip():
        return []

    if index is None or not chunks:
        return []

    # Encode query and convert to 2D numpy array float32
    query_vector = model.encode([query], show_progress_bar=False, convert_to_numpy=True).astype(np.float32)
    
    # Normalize vector for Cosine Similarity search
    norm = np.linalg.norm(query_vector)
    if norm > 0:
        query_vector = query_vector / norm

    # Bound search candidate pool
    fetch_k = min(len(chunks), max(top_k * 5, 25)) if filter_filename else min(top_k, len(chunks))

    # FAISS search
    scores, indices = index.search(query_vector, fetch_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0 and idx < len(chunks):
            chunk_data = chunks[idx].copy()
            source_file = chunk_data.get("filename") or chunk_data.get("source_file") or ""
            
            if filter_filename and source_file != filter_filename:
                continue

            chunk_data["score"] = float(score)
            results.append(chunk_data)

            if len(results) >= top_k:
                break

    # If filtering returned no results (e.g. filename mismatch), fallback to top unfiltered chunks
    if not results and filter_filename:
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0 and idx < len(chunks):
                chunk_data = chunks[idx].copy()
                chunk_data["score"] = float(score)
                results.append(chunk_data)
                if len(results) >= top_k:
                    break

    return results

