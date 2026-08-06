"""Retrieve relevant note chunks and generate a cited answer with Claude."""
import anthropic
import voyageai

from .store import VectorStore

EMBED_MODEL = "voyage-3-lite"
CHAT_MODEL = "claude-sonnet-4-5"
TOP_K = 4

SYSTEM_PROMPT = """You are a Q&A assistant over a set of Claude Code study notes.
Answer only using the provided context chunks. If the context doesn't contain
the answer, say you don't know. Always answer in Traditional Chinese (繁體中文).
Cite which note(s) you used by title at the end of your answer."""


class RagPipeline:
    def __init__(self):
        self.voyage = voyageai.Client()
        self.anthropic = anthropic.Anthropic()
        self.store = VectorStore()

    def ask(self, question: str, top_k: int = TOP_K) -> dict:
        query_embedding = self.voyage.embed(
            [question], model=EMBED_MODEL, input_type="query"
        ).embeddings[0]
        matches = self.store.search(query_embedding, top_k=top_k)

        context = "\n\n---\n\n".join(f"[{m['title']}]\n{m['text']}" for m in matches)
        user_message = f"Context:\n{context}\n\nQuestion: {question}"

        response = self.anthropic.messages.create(
            model=CHAT_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
        answer = "".join(
            block.text for block in response.content if block.type == "text"
        )

        sources = []
        seen = set()
        for m in matches:
            if m["title"] in seen:
                continue
            seen.add(m["title"])
            sources.append({"title": m["title"], "url": m["source_url"]})

        return {"answer": answer, "sources": sources}
