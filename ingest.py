"""
ingest.py - Multi-Format (PDF, TXT, DOCX, PPTX) & Multi-Document Text Extraction, Chunking, Embedding & FAISS Indexing. Updated.
"""

from typing import Tuple, List, Dict, Any, Union
from io import BytesIO
import os
import numpy as np
from pypdf import PdfReader
import docx
import pptx
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

# Gracefully import FAISS or use pure-NumPy vector index fallback if C++ wheels are missing
try:
    import faiss
    HAS_FAISS = True
except ImportError:
    HAS_FAISS = False
    class NumpyVectorIndex:
        """Pure Python/NumPy fallback vector store implementing FAISS IndexFlatIP interface."""
        def __init__(self, dimension: int):
            self.dimension = dimension
            self.vectors = None

        def add(self, vectors: np.ndarray):
            if self.vectors is None:
                self.vectors = vectors.astype(np.float32)
            else:
                self.vectors = np.vstack([self.vectors, vectors.astype(np.float32)])

        def search(self, query_vector: np.ndarray, k: int):
            scores = np.dot(self.vectors, query_vector.T).squeeze(axis=1)
            if scores.ndim == 0:
                scores = np.array([scores])
            top_k_indices = np.argsort(scores)[::-1][:k]
            top_k_scores = scores[top_k_indices]
            return np.array([top_k_scores]), np.array([top_k_indices])


# Suppress HuggingFace hub symlink warning on Windows
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


SUPPORTED_EXTENSIONS = ["pdf", "txt", "docx", "pptx"]
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


class IngestError(Exception):
    """Custom exception class for document ingestion errors."""
    pass


def load_embedding_model(model_name: str = EMBEDDING_MODEL_NAME) -> SentenceTransformer:

    """
    Loads and returns the SentenceTransformer model for generating text embeddings.
    """
    try:
        return SentenceTransformer(model_name, local_files_only=True)
    except Exception:
        try:
            return SentenceTransformer(model_name)
        except Exception:
            os.environ["HF_HUB_OFFLINE"] = "1"
            return SentenceTransformer(model_name, local_files_only=True)


def extract_text_from_pdf(pdf_source: Union[str, BytesIO]) -> List[Dict[str, Any]]:
    """Extracts text from a PDF file page by page."""
    try:
        reader = PdfReader(pdf_source)
    except Exception as e:
        raise ValueError(f"Failed to read PDF file: {str(e)}") from e

    if not reader.pages:
        raise ValueError("The uploaded PDF has no pages.")

    pages_data = []
    total_text_len = 0

    for i, page in enumerate(reader.pages):
        page_text = (page.extract_text() or "").strip()
        if page_text:
            pages_data.append({"page": i + 1, "text": page_text})
            total_text_len += len(page_text)

    if total_text_len == 0:
        raise ValueError("PDF contains no readable text. It might be scanned (image-only), empty, or password-protected.")

    return pages_data


def extract_text_from_txt(txt_source: Union[str, BytesIO]) -> List[Dict[str, Any]]:
    """Extracts text from a plain text (.txt) file with encoding error handling."""
    try:
        if isinstance(txt_source, BytesIO):
            content_bytes = txt_source.read()
        elif hasattr(txt_source, "read"):
            content_bytes = txt_source.read()
        else:
            with open(txt_source, "rb") as f:
                content_bytes = f.read()

        try:
            text_content = content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            text_content = content_bytes.decode("latin-1", errors="ignore")

        text_content = text_content.strip()
    except Exception as e:
        raise ValueError(f"Failed to read TXT file: {str(e)}") from e

    if not text_content:
        raise ValueError("The uploaded TXT file is empty or contains no readable text.")

    return [{"page": 1, "text": text_content}]


def extract_text_from_docx(docx_source: Union[str, BytesIO]) -> List[Dict[str, Any]]:
    """Extracts text from a Word document (.docx) paragraph by paragraph."""
    try:
        doc = docx.Document(docx_source)
        paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

        # Also extract table cells text
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                if row_text:
                    paragraphs.append(row_text)

        full_text = "\n\n".join(paragraphs).strip()
    except Exception as e:
        raise ValueError(f"Failed to read DOCX file: {str(e)}") from e

    if not full_text:
        raise ValueError("The uploaded DOCX file contains no readable text.")

    return [{"page": 1, "text": full_text}]


def extract_text_from_pptx(pptx_source: Union[str, BytesIO]) -> List[Dict[str, Any]]:
    """Extracts text from a PowerPoint presentation (.pptx) slide by slide."""
    try:
        prs = pptx.Presentation(pptx_source)
        slides_data = []
        total_text_len = 0

        for i, slide in enumerate(prs.slides):
            slide_texts = []
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    slide_texts.append(shape.text.strip())
                elif hasattr(shape, "table"):
                    for row in shape.table.rows:
                        row_text = " | ".join(cell.text.strip() for cell in row.cells if cell.text.strip())
                        if row_text:
                            slide_texts.append(row_text)

            slide_full_text = "\n".join(slide_texts).strip()
            if slide_full_text:
                slides_data.append({"page": i + 1, "text": slide_full_text})
                total_text_len += len(slide_full_text)

    except Exception as e:
        raise ValueError(f"Failed to read PPTX file: {str(e)}") from e

    if total_text_len == 0:
        raise ValueError("The uploaded PPTX presentation contains no readable text.")

    return slides_data


def extract_text_by_format(file_source: Union[str, BytesIO], filename: str) -> List[Dict[str, Any]]:
    """
    Detects format from filename extension (.pdf, .txt, .docx, .pptx) and runs corresponding extractor.
    """
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        return extract_text_from_pdf(file_source)
    elif ext == "txt":
        return extract_text_from_txt(file_source)
    elif ext == "docx":
        return extract_text_from_docx(file_source)
    elif ext == "pptx":
        return extract_text_from_pptx(file_source)
    else:
        raise ValueError(f"Unsupported file format '.{ext}'. Please upload a PDF, TXT, DOCX, or PPTX document.")


def split_text_into_chunks(
    pages_data: List[Dict[str, Any]],
    filename: str = "document",
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> List[Dict[str, Any]]:
    """
    Splits page/slide-level text into smaller text chunks using RecursiveCharacterTextSplitter.
    Tags each chunk with source_file metadata.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )

    chunks = []
    chunk_id = 0

    for page_info in pages_data:
        page_num = page_info["page"]
        page_text = page_info["text"]

        page_chunks = splitter.split_text(page_text)
        for text in page_chunks:
            if text.strip():
                chunks.append({
                    "id": chunk_id,
                    "source_file": filename,
                    "filename": filename,
                    "page": page_num,
                    "text": text.strip()
                })
                chunk_id += 1

    return chunks


def build_faiss_index(
    chunks: List[Dict[str, Any]],
    model: SentenceTransformer
) -> Tuple[Any, List[Dict[str, Any]]]:
    """Embeds chunk texts and constructs a FAISS IndexFlatIP (or Numpy fallback)."""
    if not chunks:
        raise ValueError("No text chunks available to index.")

    # Update chunk IDs sequentially across multi-doc collections
    for idx, c in enumerate(chunks):
        c["id"] = idx

    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False, convert_to_numpy=True).astype(np.float32)

    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1e-10
    embeddings = embeddings / norms

    dimension = embeddings.shape[1]
    if HAS_FAISS:
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
    else:
        index = NumpyVectorIndex(dimension)
        index.add(embeddings)

    return index, chunks


def process_multiple_documents(
    documents_list: List[Tuple[Union[str, BytesIO], str]],
    embedding_model: SentenceTransformer,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> Tuple[Any, List[Dict[str, Any]]]:
    """
    Processes multiple documents, tagging each chunk with source_file metadata,
    and merging all chunks into a SINGLE unified FAISS index.
    """
    if not documents_list:
        raise ValueError("No documents provided for ingestion.")

    all_chunks = []
    for file_source, filename in documents_list:
        pages_data = extract_text_by_format(file_source, filename)
        doc_chunks = split_text_into_chunks(pages_data, filename=filename, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        all_chunks.extend(doc_chunks)

    index, stored_chunks = build_faiss_index(all_chunks, embedding_model)
    return index, stored_chunks


def process_document(
    file_source: Union[str, BytesIO],
    filename: str,
    embedding_model: SentenceTransformer,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> Tuple[Any, List[Dict[str, Any]]]:
    """Single document process wrapper."""
    return process_multiple_documents([(file_source, filename)], embedding_model, chunk_size, chunk_overlap)


def process_pdf(
    pdf_source: Union[str, BytesIO],
    embedding_model: SentenceTransformer,
    chunk_size: int = 500,
    chunk_overlap: int = 50
) -> Tuple[Any, List[Dict[str, Any]]]:
    """Backwards compatibility wrapper for PDF files."""
    return process_document(pdf_source, "document.pdf", embedding_model, chunk_size, chunk_overlap)


def add_documents(
    existing_chunks: List[Dict[str, Any]],
    existing_index: Any,
    file_bytes: bytes,
    filename: str,
    model: SentenceTransformer
) -> Tuple[List[Dict[str, Any]], Any]:
    """
    Ingests a new document from bytes, extracts text, chunks it, and appends to existing chunks/FAISS index.
    Returns (merged_chunks, merged_index).
    """
    try:
        pages_data = extract_text_by_format(BytesIO(file_bytes), filename)
        new_chunks = split_text_into_chunks(pages_data, filename=filename)
        all_chunks = list(existing_chunks) + new_chunks
        merged_index, merged_chunks = build_faiss_index(all_chunks, model)
        return merged_chunks, merged_index
    except Exception as e:
        raise IngestError(f"Error processing {filename}: {str(e)}") from e

