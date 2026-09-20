import os
import re
from typing import List, Tuple

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, "..", "knowledge_base", "faq.txt")


def _load_and_chunk_kb(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()

    parts = raw.split("TITLE:")
    chunks = []

    for part in parts:
        part = part.strip()
        if part:
            chunks.append("TITLE:" + part)

    return chunks


def _tokens(text: str) -> set:
    return set(re.findall(r"\b[a-zA-Z0-9]+\b", text.lower()))


def _similarity(query: str, text: str) -> float:
    query_tokens = _tokens(query)
    text_tokens = _tokens(text)

    if not query_tokens or not text_tokens:
        return 0.0

    return len(query_tokens & text_tokens) / len(query_tokens)


class KnowledgeBase:
    def __init__(self):
        self.chunks: List[str] = _load_and_chunk_kb(KB_PATH)

    def search(
        self,
        query: str,
        k: int = 3,
        min_score: float = 0.25
    ) -> List[Tuple[str, float]]:

        results = []

        for chunk in self.chunks:
            score = _similarity(query, chunk)

            if score >= min_score:
                results.append((chunk, score))

        results.sort(key=lambda x: x[1], reverse=True)

        return results[:k]


_kb_instance: KnowledgeBase = None


def get_knowledge_base() -> KnowledgeBase:
    global _kb_instance

    if _kb_instance is None:
        _kb_instance = KnowledgeBase()

    return _kb_instance