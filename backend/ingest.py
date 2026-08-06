"""Chunk data/notes/*.md, embed with Voyage AI, and write data/index.json.

Run directly, or via headless Claude Code:
    claude -p "Re-run ingestion on data/notes and rebuild the index" \
        --allowedTools "Bash(python backend/ingest.py)"
"""
import json
import re
from pathlib import Path

import voyageai
from dotenv import load_dotenv

load_dotenv()

NOTES_DIR = Path(__file__).resolve().parent.parent / "data" / "notes"
INDEX_PATH = Path(__file__).resolve().parent.parent / "data" / "index.json"
EMBED_MODEL = "voyage-3-lite"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n(.*)$", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    raw_meta, body = match.groups()
    meta = {}
    for line in raw_meta.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        meta[key.strip()] = value.strip().strip('"')
    return meta, body


def chunk_by_heading(body: str) -> list[str]:
    """Split on level-2 (##) headings, keeping the level-1 title with every chunk."""
    lines = body.splitlines()
    title_line = ""
    if lines and lines[0].startswith("# "):
        title_line = lines[0]
        lines = lines[1:]
    body = "\n".join(lines)

    sections = re.split(r"\n(?=## )", body.strip())
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        chunk_text = f"{title_line}\n\n{section}".strip() if title_line else section
        chunks.append(chunk_text)
    return chunks


def build_index() -> list[dict]:
    files = sorted(NOTES_DIR.glob("*.md"))
    if not files:
        raise SystemExit(f"No notes found in {NOTES_DIR}")

    records = []
    for path in files:
        raw = path.read_text(encoding="utf-8")
        meta, body = parse_frontmatter(raw)
        title = meta.get("title", path.stem)
        source_url = meta.get("source_url", "")
        for i, chunk in enumerate(chunk_by_heading(body)):
            records.append(
                {
                    "id": f"{path.stem}-{i}",
                    "title": title,
                    "source_url": source_url,
                    "text": chunk,
                }
            )

    client = voyageai.Client()
    texts = [r["text"] for r in records]
    result = client.embed(texts, model=EMBED_MODEL, input_type="document")
    for record, embedding in zip(records, result.embeddings):
        record["embedding"] = embedding

    return records


def main():
    records = build_index()
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    INDEX_PATH.write_text(json.dumps(records, ensure_ascii=False), encoding="utf-8")
    print(
        f"Indexed {len(records)} chunks from {len(list(NOTES_DIR.glob('*.md')))} "
        f"notes -> {INDEX_PATH}"
    )


if __name__ == "__main__":
    main()
