"""Load data/index.json and perform cosine-similarity search over chunk embeddings."""
import json
from pathlib import Path

import numpy as np

INDEX_PATH = Path(__file__).resolve().parent.parent / "data" / "index.json"


class VectorStore:
    def __init__(self, index_path: Path = INDEX_PATH):
        if not index_path.exists():
            raise FileNotFoundError(
                f"{index_path} not found. Run `python backend/ingest.py` first."
            )
        records = json.loads(index_path.read_text(encoding="utf-8"))
        self.records = records
        self.embeddings = np.array([r["embedding"] for r in records], dtype=np.float32)
        norms = np.linalg.norm(self.embeddings, axis=1, keepdims=True)
        self._normalized = self.embeddings / np.clip(norms, 1e-10, None)

    def search(self, query_embedding: list[float], top_k: int = 4) -> list[dict]:
        query = np.array(query_embedding, dtype=np.float32)
        query = query / max(float(np.linalg.norm(query)), 1e-10)
        scores = self._normalized @ query
        top_indices = np.argsort(-scores)[:top_k]
        return [{**self.records[i], "score": float(scores[i])} for i in top_indices]
