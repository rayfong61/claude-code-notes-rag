"""Retrieve relevant note chunks and generate a cited answer with Claude."""
import logging

import anthropic
import voyageai

from .store import VectorStore

logger = logging.getLogger(__name__)

EMBED_MODEL = "voyage-3-lite"
CHAT_MODEL = "claude-sonnet-4-5"
TOP_K = 4

# Below this cosine similarity, the best match is treated as "not actually
# relevant" and we skip calling Claude rather than let it guess from a
# tenuous chunk (e.g. one-word or off-topic questions). Calibrated against
# real voyage-3-lite scores: an on-topic question like "Hooks 是什麼？" scores
# ~0.78 on its best chunk, while a garbage one-letter query still scores
# ~0.45 (embeddings of short/near-empty text land close to everything).
MIN_RELEVANCE_SCORE = 0.55
NO_MATCH_ANSWER = "這個問題在筆記裡找不到相關內容，麻煩換個問題或提供更多細節。"

SYSTEM_PROMPT = """You are a Q&A assistant over a set of Claude Code study notes,
having a multi-turn conversation with the user. Answer only using the provided
context chunks for the current question; you may also use earlier turns in the
conversation to resolve references like "that" or follow-up questions. If the
context doesn't contain the answer, say you don't know. Always answer in
Traditional Chinese (繁體中文). Cite which note(s) you used by title at the end
of your answer."""


class RagPipeline:
    def __init__(self):
        self.voyage = voyageai.Client()
        self.anthropic = anthropic.Anthropic()
        self.store = VectorStore()

    def _retrieve(self, question: str, history: list[dict], top_k: int):
        query_embedding = self.voyage.embed(
            [question], model=EMBED_MODEL, input_type="query"
        ).embeddings[0]
        matches = self.store.search(query_embedding, top_k=top_k)
        logger.info(
            "retrieval question=%r matches=%s",
            question,
            [(m["title"], round(m["score"], 3)) for m in matches],
        )

        context = "\n\n---\n\n".join(f"[{m['title']}]\n{m['text']}" for m in matches)
        user_message = f"Context:\n{context}\n\nQuestion: {question}"

        messages = [{"role": h["role"], "content": h["content"]} for h in history]
        messages.append({"role": "user", "content": user_message})
        return messages, matches

    @staticmethod
    def _is_relevant(matches: list[dict]) -> bool:
        return bool(matches) and matches[0]["score"] >= MIN_RELEVANCE_SCORE

    @staticmethod
    def _sources_from_matches(matches: list[dict]) -> list[dict]:
        sources = []
        seen = set()
        for m in matches:
            if m["title"] in seen:
                continue
            seen.add(m["title"])
            sources.append({"title": m["title"], "url": m["source_url"]})
        return sources

    def ask(self, question: str, history: list[dict] | None = None, top_k: int = TOP_K) -> dict:
        messages, matches = self._retrieve(question, history or [], top_k)

        if not self._is_relevant(matches):
            logger.info("question=%r has no relevant match, skipping Claude call", question)
            return {"answer": NO_MATCH_ANSWER, "sources": []}

        response = self.anthropic.messages.create(
            model=CHAT_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        )
        answer = "".join(
            block.text for block in response.content if block.type == "text"
        )

        return {"answer": answer, "sources": self._sources_from_matches(matches)}

    def ask_stream(self, question: str, history: list[dict] | None = None, top_k: int = TOP_K):
        """Yields {"type": "delta", "text": ...} chunks as Claude generates the
        answer, then a final {"type": "done", "sources": [...]}."""
        messages, matches = self._retrieve(question, history or [], top_k)

        if not self._is_relevant(matches):
            logger.info("question=%r has no relevant match, skipping Claude call", question)
            yield {"type": "delta", "text": NO_MATCH_ANSWER}
            yield {"type": "done", "sources": []}
            return

        with self.anthropic.messages.stream(
            model=CHAT_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                yield {"type": "delta", "text": text}

        yield {"type": "done", "sources": self._sources_from_matches(matches)}
