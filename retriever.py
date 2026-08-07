"""
retriever.py - Vector Similarity Search using FAISS and SentenceTransformer embeddings.
"""

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss


def retrieve_chunks(
    query: str,
    index: faiss.IndexFlatIP,
    chunks: List[Dict[str, Any]],
    model: SentenceTransformer,
    top_k: int = 4
) -> List[Dict[str, Any]]:
    """
    Embeds the user query, searches the FAISS index for top_k similar vectors,
    and returns matching chunk dictionaries with similarity scores.
    
    Args:
        query: User input question string.
        index: Trained FAISS IndexFlatIP.
        chunks: List of chunk metadata dicts corresponding to FAISS vector indices.
        model: SentenceTransformer embedding model.
        top_k: Number of top chunks to retrieve (default: 4).
        
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

    # Bound top_k to total available chunks
    actual_k = min(top_k, len(chunks))


    # FAISS search
    scores, indices = index.search(query_vector, actual_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx >= 0 and idx < len(chunks):
            chunk_data = chunks[idx].copy()
            # Score is Cosine Similarity (range -1.0 to 1.0, practically 0.0 to 1.0)
            chunk_data["score"] = float(score)
            results.append(chunk_data)

    return results
