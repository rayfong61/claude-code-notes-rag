"""Retrieve relevant note chunks and generate a cited answer with Claude."""
import logging

import anthropic
import voyageai

from .store import VectorStore

logger = logging.getLogger(__name__)

EMBED_MODEL = "voyage-3-lite"
CHAT_MODEL = "claude-sonnet-4-5"
TOP_K = 4

# Above ~0.55, a chunk's cosine similarity to the question is usually a
# genuine match; below that, retrieval is "reaching" and the chunk probably
# doesn't answer the question. Claude sees this number directly (see
# SYSTEM_PROMPT_TEMPLATE) instead of a Python-side hard cutoff, so it can
# still answer meta-questions about the note collection itself (e.g. "how
# many notes are there") even when no single chunk scores well for them.
SYSTEM_PROMPT_TEMPLATE = """You are a Q&A assistant over a fixed set of Claude Code
study notes, having a multi-turn conversation with the user. The notes cover
exactly these topics:
{note_titles}

For each question you're given retrieved context chunks, each tagged with a
relevance score from 0 to 1 (cosine similarity to the question). Scores above
~0.55 usually mean the chunk is genuinely relevant; lower scores mean
retrieval was reaching and the chunk probably does NOT answer the question —
don't build your answer around a low-scoring chunk.

- If the question is about the note collection itself (e.g. how many notes
  exist, what topics are covered), answer directly from the topic list above.
- If a chunk's content actually answers the question, use it and cite the
  note title(s) by name at the end of your answer.
- If neither the topic list nor the retrieved chunks can answer the question,
  say so plainly and suggest one or two topics from the list above instead of
  guessing from irrelevant chunks.
- You may use earlier turns in the conversation to resolve references like
  "that" or follow-up questions.

Always answer in Traditional Chinese (繁體中文)."""


class RagPipeline:
    def __init__(self):
        self.voyage = voyageai.Client()
        self.anthropic = anthropic.Anthropic()
        self.store = VectorStore()

    def _system_prompt(self) -> str:
        titles = sorted({r["title"] for r in self.store.records})
        return SYSTEM_PROMPT_TEMPLATE.format(
            note_titles="\n".join(f"- {t}" for t in titles)
        )

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

        context = "\n\n---\n\n".join(
            f"[{m['title']} | relevance={m['score']:.2f}]\n{m['text']}" for m in matches
        )
        user_message = f"Context:\n{context}\n\nQuestion: {question}"

        messages = [{"role": h["role"], "content": h["content"]} for h in history]
        messages.append({"role": "user", "content": user_message})
        return messages, matches

    @staticmethod
    def _sources_from_matches(matches: list[dict], answer: str) -> list[dict]:
        """Only surface a source if Claude actually cited its title in the
        answer — otherwise a retrieved-but-unused chunk (e.g. for a question
        it answered from the topic list, or declined) looks like a citation
        it never made."""
        sources = []
        seen = set()
        for m in matches:
            if m["title"] in seen or m["title"] not in answer:
                continue
            seen.add(m["title"])
            sources.append({"title": m["title"], "url": m["source_url"]})
        return sources

    def ask(self, question: str, history: list[dict] | None = None, top_k: int = TOP_K) -> dict:
        messages, matches = self._retrieve(question, history or [], top_k)

        response = self.anthropic.messages.create(
            model=CHAT_MODEL,
            max_tokens=1024,
            system=self._system_prompt(),
            messages=messages,
        )
        answer = "".join(
            block.text for block in response.content if block.type == "text"
        )

        return {"answer": answer, "sources": self._sources_from_matches(matches, answer)}

    def ask_stream(self, question: str, history: list[dict] | None = None, top_k: int = TOP_K):
        """Yields {"type": "delta", "text": ...} chunks as Claude generates the
        answer, then a final {"type": "done", "sources": [...]}."""
        messages, matches = self._retrieve(question, history or [], top_k)

        answer_parts = []
        with self.anthropic.messages.stream(
            model=CHAT_MODEL,
            max_tokens=1024,
            system=self._system_prompt(),
            messages=messages,
        ) as stream:
            for text in stream.text_stream:
                answer_parts.append(text)
                yield {"type": "delta", "text": text}

        answer = "".join(answer_parts)
        yield {"type": "done", "sources": self._sources_from_matches(matches, answer)}
