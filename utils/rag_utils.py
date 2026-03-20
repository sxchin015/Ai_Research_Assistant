import io
import logging
import os
import numpy as np

logger = logging.getLogger(__name__)

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from config.config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS, MIN_RELEVANCE_SCORE
from models.embeddings import embed_texts, embed_query


def extract_text(file_bytes, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        if not PDF_AVAILABLE:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            pages = [p.extract_text() for p in pdf.pages if p.extract_text()]
        return "\n".join(pages)
    else:
        try:
            return file_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return file_bytes.decode("latin-1")


def chunk_text(text):
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        chunk = text[start : start + CHUNK_SIZE].strip()
        if chunk:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


class FAISSIndex:
    def __init__(self):
        self.index = None
        self.chunks = []

    @property
    def is_built(self):
        return self.index is not None and len(self.chunks) > 0

    def build(self, chunks):
        if not FAISS_AVAILABLE:
            raise RuntimeError("faiss-cpu not installed. Run: pip install faiss-cpu")
        vectors = embed_texts(chunks)
        matrix = np.array(vectors, dtype="float32")
        faiss.normalize_L2(matrix)
        self.index = faiss.IndexFlatIP(matrix.shape[1])
        self.index.add(matrix)
        self.chunks = chunks

    def search(self, query, top_k=TOP_K_RESULTS):
        if not self.is_built:
            return []
        q = np.array([embed_query(query)], dtype="float32")
        faiss.normalize_L2(q)
        scores, indices = self.index.search(q, min(top_k, len(self.chunks)))
        return [(self.chunks[i], float(s)) for s, i in zip(scores[0], indices[0]) if i != -1]


def build_index_from_file(file_bytes, filename):
    text = extract_text(file_bytes, filename)
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("No text could be extracted from the file.")
    idx = FAISSIndex()
    idx.build(chunks)
    return idx


def retrieve_context(query, faiss_index):
    if not faiss_index.is_built:
        return "", False
    try:
        results = faiss_index.search(query)
        relevant = [(c, s) for c, s in results if s >= MIN_RELEVANCE_SCORE]
        if not relevant:
            return "", False
        parts = [f"[Chunk {i+1} | score {s:.2f}]\n{c}" for i, (c, s) in enumerate(relevant)]
        return "\n\n".join(parts), True
    except Exception as exc:
        logger.error("RAG retrieval error: %s", exc)
        return "", False
