from __future__ import annotations

import json
import math
from collections import Counter
from pathlib import Path
from typing import Dict, List

from core.settings import SETTINGS
from indexing.chunking import chunk_text
from indexing.ingest import ingest_pack


class VectorStore:
    def __init__(self, pack_name: str, db_path: Path, vector_path: Path) -> None:
        self.pack_name = pack_name
        self.db_path = db_path
        self.vector_path = vector_path
        self._vectors: Dict[str, Dict[str, int]] = {}
        self._metadata: Dict[str, dict] = {}

    @classmethod
    def from_pack(cls, pack_name: str) -> "VectorStore":
        db_path = SETTINGS.data_dir / "db" / f"{pack_name}.json"
        vector_path = SETTINGS.data_dir / "db" / f"{pack_name}_vectors.json"
        store = cls(pack_name, db_path, vector_path)
        store._load()
        return store

    def build(self) -> None:
        pack_dir = SETTINGS.packs_dir / self.pack_name
        docs = ingest_pack(pack_dir)
        chunk_id = 0
        for doc in docs:
            chunks = chunk_text(doc["content"])
            for chunk in chunks:
                chunk_id += 1
                chunk_key = f"{self.pack_name}-{chunk_id}"
                self._metadata[chunk_key] = {
                    "title": doc["path"].name,
                    "source": str(doc["path"]),
                    "excerpt": chunk[:300],
                }
                self._vectors[chunk_key] = _embed_text(chunk)
        self._save()

    def search(self, query: str, k: int = 5) -> List[dict]:
        if not self._vectors:
            return []
        query_vector = _embed_text(query)
        scored: List[tuple[str, float]] = []
        for key, vector in self._vectors.items():
            score = _cosine_similarity(query_vector, vector)
            scored.append((key, score))
        scored.sort(key=lambda item: item[1], reverse=True)
        results = []
        for key, score in scored[:k]:
            if score <= 0:
                continue
            data = dict(self._metadata[key])
            data["score"] = score
            results.append(data)
        return results

    def _save(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.db_path.write_text(json.dumps(self._metadata, indent=2))
        self.vector_path.write_text(json.dumps(self._vectors, indent=2))

    def _load(self) -> None:
        if self.db_path.exists():
            self._metadata = json.loads(self.db_path.read_text())
        if self.vector_path.exists():
            self._vectors = json.loads(self.vector_path.read_text())


def _embed_text(text: str) -> Dict[str, int]:
    tokens = [token.lower() for token in text.split() if token.isalpha()]
    return dict(Counter(tokens))


def _cosine_similarity(a: Dict[str, int], b: Dict[str, int]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    dot = sum(a[token] * b[token] for token in common)
    norm_a = math.sqrt(sum(value * value for value in a.values()))
    norm_b = math.sqrt(sum(value * value for value in b.values()))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)
