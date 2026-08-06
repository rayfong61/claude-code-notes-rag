"""Tests for the notes RAG pipeline.

Unit tests (chunking, retrieval ranking) run offline with no API calls.
The /ask smoke test hits the real Voyage + Anthropic APIs and is skipped
automatically if the required API keys aren't set.
"""
import json
import os
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ingest import chunk_by_heading, parse_frontmatter
from backend.rag import RagPipeline
from backend.store import VectorStore

HAS_API_KEYS = bool(os.environ.get("ANTHROPIC_API_KEY")) and bool(
    os.environ.get("VOYAGE_API_KEY")
)


def test_parse_frontmatter_extracts_title_and_url():
    raw = (
        "---\n"
        'title: "Example Note"\n'
        "source_url: https://example.com/x\n"
        "---\n"
        "# Example Note\n\nbody text\n"
    )
    meta, body = parse_frontmatter(raw)
    assert meta["title"] == "Example Note"
    assert meta["source_url"] == "https://example.com/x"
    assert body.strip().startswith("# Example Note")


def test_parse_frontmatter_handles_missing_frontmatter():
    raw = "# Just a title\n\nbody\n"
    meta, body = parse_frontmatter(raw)
    assert meta == {}
    assert body == raw


def test_chunk_by_heading_splits_on_level_two_headings():
    body = "# Title\n\n## Section One\ncontent one\n\n## Section Two\ncontent two\n"
    chunks = chunk_by_heading(body)
    assert len(chunks) == 2
    assert chunks[0].startswith("# Title\n\n## Section One")
    assert "content one" in chunks[0]
    assert chunks[1].startswith("# Title\n\n## Section Two")
    assert "content two" in chunks[1]


def test_chunk_by_heading_keeps_single_section_without_subheadings():
    body = "# Title\n\njust one section, no ## headings\n"
    chunks = chunk_by_heading(body)
    assert len(chunks) == 1
    assert "just one section" in chunks[0]


def test_vector_store_search_returns_closest_match(tmp_path):
    fake_index = [
        {"id": "a", "title": "Hooks", "source_url": "u1", "text": "hooks content", "embedding": [1.0, 0.0, 0.0]},
        {"id": "b", "title": "Plugins", "source_url": "u2", "text": "plugins content", "embedding": [0.0, 1.0, 0.0]},
        {"id": "c", "title": "CLAUDE.md", "source_url": "u3", "text": "claude md content", "embedding": [0.0, 0.0, 1.0]},
    ]
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(fake_index), encoding="utf-8")

    store = VectorStore(index_path=index_path)
    results = store.search([0.9, 0.1, 0.0], top_k=1)

    assert results[0]["title"] == "Hooks"
    assert results[0]["score"] > 0.9


def test_vector_store_top_k_orders_by_score(tmp_path):
    fake_index = [
        {"id": "a", "title": "A", "source_url": "u1", "text": "a", "embedding": [1.0, 0.0]},
        {"id": "b", "title": "B", "source_url": "u2", "text": "b", "embedding": [0.7, 0.7]},
        {"id": "c", "title": "C", "source_url": "u3", "text": "c", "embedding": [0.0, 1.0]},
    ]
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(fake_index), encoding="utf-8")

    store = VectorStore(index_path=index_path)
    results = store.search([1.0, 0.0], top_k=3)
    titles = [r["title"] for r in results]

    assert titles == ["A", "B", "C"]


@pytest.mark.skipif(not HAS_API_KEYS, reason="requires ANTHROPIC_API_KEY and VOYAGE_API_KEY")
def test_ask_endpoint_returns_cited_answer():
    from fastapi.testclient import TestClient

    from backend.main import app

    client = TestClient(app)
    response = client.post("/ask", json={"question": "Claude Code 的 Hooks 是什麼？"})

    assert response.status_code == 200
    body = response.json()
    assert body["answer"]
    assert len(body["sources"]) > 0
    assert any("Hook" in s["title"] for s in body["sources"])


class _FakeVoyageClient:
    def embed(self, texts, model, input_type):
        class _Result:
            embeddings = [[1.0, 0.0, 0.0] for _ in texts]

        return _Result()


class _FakeAnthropicMessages:
    def __init__(self):
        self.last_call = None

    def create(self, **kwargs):
        self.last_call = kwargs

        class _Block:
            type = "text"
            text = "測試回答，引用 CLAUDE.md。"

        class _Response:
            content = [_Block()]

        return _Response()


class _FakeAnthropicClient:
    def __init__(self):
        self.messages = _FakeAnthropicMessages()


def test_rag_pipeline_forwards_history_to_claude(tmp_path):
    """Unit test with fake API clients: no network calls, no rate limits."""
    fake_index = [
        {"id": "a", "title": "Hooks", "source_url": "u1", "text": "hooks content", "embedding": [1.0, 0.0, 0.0]},
    ]
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(fake_index), encoding="utf-8")

    pipeline = RagPipeline.__new__(RagPipeline)
    pipeline.voyage = _FakeVoyageClient()
    pipeline.anthropic = _FakeAnthropicClient()
    pipeline.store = VectorStore(index_path=index_path)

    history = [
        {"role": "user", "content": "Claude Code 的 Hooks 是什麼？"},
        {"role": "assistant", "content": "Hooks 是強制執行的機制。"},
    ]
    result = pipeline.ask("它跟 CLAUDE.md 有什麼不同？", history=history)

    sent_messages = pipeline.anthropic.messages.last_call["messages"]
    assert sent_messages[0] == history[0]
    assert sent_messages[1] == history[1]
    assert sent_messages[-1]["role"] == "user"
    assert "它跟 CLAUDE.md 有什麼不同" in sent_messages[-1]["content"]
    assert result["answer"] == "測試回答，引用 CLAUDE.md。"


def test_ask_puts_topic_list_in_system_prompt_and_scores_in_context(tmp_path):
    """Claude, not a Python-side score cutoff, judges relevance now — so it
    needs the full topic list (for meta-questions like "how many notes are
    there") and per-chunk relevance scores (to avoid trusting weak matches)."""
    fake_index = [
        {"id": "a", "title": "Hooks", "source_url": "u1", "text": "hooks content", "embedding": [1.0, 0.0, 0.0]},
        {"id": "b", "title": "Plugins", "source_url": "u2", "text": "plugins content", "embedding": [0.0, 1.0, 0.0]},
    ]
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(fake_index), encoding="utf-8")

    pipeline = RagPipeline.__new__(RagPipeline)
    pipeline.voyage = _FakeVoyageClient()
    pipeline.anthropic = _FakeAnthropicClient()
    pipeline.store = VectorStore(index_path=index_path)

    pipeline.ask("隨便問點什麼")

    call = pipeline.anthropic.messages.last_call
    assert "Hooks" in call["system"]
    assert "Plugins" in call["system"]

    user_message = call["messages"][-1]["content"]
    assert "relevance=" in user_message


class _FakeAnthropicMessagesWithAnswer:
    """Fixed-answer fake client so tests control exactly what Claude 'said'."""

    def __init__(self, answer_text: str):
        self.answer_text = answer_text
        self.last_call = None

    def create(self, **kwargs):
        self.last_call = kwargs

        class _Block:
            type = "text"

        block = _Block()
        block.text = self.answer_text

        class _Response:
            content = [block]

        return _Response()


def _two_chunk_index(tmp_path):
    fake_index = [
        {"id": "a", "title": "Hooks", "source_url": "u1", "text": "hooks content", "embedding": [1.0, 0.0, 0.0]},
        {"id": "b", "title": "Plugins", "source_url": "u2", "text": "plugins content", "embedding": [0.9, 0.1, 0.0]},
    ]
    index_path = tmp_path / "index.json"
    index_path.write_text(json.dumps(fake_index), encoding="utf-8")
    return index_path


def test_sources_exclude_titles_the_answer_never_mentions(tmp_path):
    pipeline = RagPipeline.__new__(RagPipeline)
    pipeline.voyage = _FakeVoyageClient()
    pipeline.anthropic = _FakeAnthropicClient()  # fixed answer mentions neither "Hooks" nor "Plugins"
    pipeline.store = VectorStore(index_path=_two_chunk_index(tmp_path))

    result = pipeline.ask("t")

    assert result["sources"] == []


class _FakeAnthropicClientWithAnswer:
    def __init__(self, answer_text: str):
        self.messages = _FakeAnthropicMessagesWithAnswer(answer_text)


def test_sources_include_titles_the_answer_actually_cites(tmp_path):
    pipeline = RagPipeline.__new__(RagPipeline)
    pipeline.voyage = _FakeVoyageClient()
    pipeline.anthropic = _FakeAnthropicClientWithAnswer("依據 Hooks 這篇筆記，答案是...")
    pipeline.store = VectorStore(index_path=_two_chunk_index(tmp_path))

    result = pipeline.ask("Hooks 是什麼？")

    assert result["sources"] == [{"title": "Hooks", "url": "u1"}]


def test_ask_stream_endpoint_emits_error_event_on_exception(monkeypatch):
    """A mid-stream exception (e.g. a rate limit) must surface as a clean
    SSE error event instead of crashing the connection silently."""
    import backend.main as main_module

    class _FailingPipeline:
        def ask_stream(self, question, history=None, top_k=4):
            yield {"type": "delta", "text": "部分回答"}
            raise RuntimeError("boom")

    monkeypatch.setattr(main_module, "get_pipeline", lambda: _FailingPipeline())

    from fastapi.testclient import TestClient

    client = TestClient(main_module.app)
    response = client.post("/ask/stream", json={"question": "test"})

    assert response.status_code == 200
    assert '"type": "delta"' in response.text
    assert '"type": "error"' in response.text
