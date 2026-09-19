"""
Retrieval-Augmented Generation (RAG) over the company knowledge base.

Loads knowledge_base/faq.txt, splits it into topic chunks (split on the
"TITLE:" markers), embeds each chunk with a sentence-transformers model,
and builds a FAISS index for similarity search. The index and chunk text
are cached to disk so we don't have to re-embed on every server restart.
"""

import os
import pickle
from typing import List, Tuple

import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "..", "knowledge_base", "faq.txt")
CACHE_DIR = os.path.join(BASE_DIR, "faiss_cache")
INDEX_PATH = os.path.join(CACHE_DIR, "index.faiss")
CHUNKS_PATH = os.path.join(CACHE_DIR, "chunks.pkl")

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


def _load_and_chunk_kb(path: str) -> List[str]:
    """Split the knowledge base file into chunks, one per TITLE section."""
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    # Each chunk starts with a line beginning "TITLE:"
    parts = raw.split("TITLE:")
    chunks = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        chunks.append("TITLE:" + part)
    return chunks


class KnowledgeBase:
    """Wraps a FAISS index over embedded knowledge-base chunks."""

    def __init__(self):
        self.model = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.chunks: List[str] = []
        self.index: faiss.Index = None
        self._load_or_build()

    def _load_or_build(self):
        kb_mtime = os.path.getmtime(KB_PATH)
        cache_is_fresh = (
            os.path.exists(INDEX_PATH)
            and os.path.exists(CHUNKS_PATH)
            and os.path.getmtime(CHUNKS_PATH) > kb_mtime
        )

        if cache_is_fresh:
            self.index = faiss.read_index(INDEX_PATH)
            with open(CHUNKS_PATH, "rb") as f:
                self.chunks = pickle.load(f)
            return

        # (Re)build the index from scratch.
        self.chunks = _load_and_chunk_kb(KB_PATH)
        embeddings = self.model.encode(self.chunks, convert_to_numpy=True)
        embeddings = embeddings.astype("float32")
        faiss.normalize_L2(embeddings)

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # cosine similarity via normalized IP
        self.index.add(embeddings)

        os.makedirs(CACHE_DIR, exist_ok=True)
        faiss.write_index(self.index, INDEX_PATH)
        with open(CHUNKS_PATH, "wb") as f:
            pickle.dump(self.chunks, f)

    def search(self, query: str, k: int = 3, min_score: float = 0.25) -> List[Tuple[str, float]]:
        """Return up to k (chunk_text, score) pairs relevant to the query."""
        if self.index is None or self.index.ntotal == 0:
            return []

        query_vec = self.model.encode([query], convert_to_numpy=True).astype("float32")
        faiss.normalize_L2(query_vec)

        k = min(k, self.index.ntotal)
        scores, indices = self.index.search(query_vec, k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            if score < min_score:
                continue
            results.append((self.chunks[idx], float(score)))
        return results


# Module-level singleton so the model/index is loaded once per process.
_kb_instance: KnowledgeBase = None


def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance
    if _kb_instance is None:
        _kb_instance = KnowledgeBase()
    return _kb_instance
