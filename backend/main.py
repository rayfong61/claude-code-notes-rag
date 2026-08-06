"""FastAPI app exposing the Claude Code notes RAG pipeline."""
import json
import logging
import sys

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .rag import RagPipeline

load_dotenv()

# Windows consoles default to a legacy codepage (e.g. cp950) that can't
# render the Chinese text in our logs; force UTF-8 so log output is legible.
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="Claude Code Notes RAG")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

_pipeline: RagPipeline | None = None


def get_pipeline() -> RagPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RagPipeline()
    return _pipeline


class HistoryMessage(BaseModel):
    role: str
    content: str


class AskRequest(BaseModel):
    question: str
    history: list[HistoryMessage] = []


class Source(BaseModel):
    title: str
    url: str


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    history = [h.model_dump() for h in request.history]
    logger.info("POST /ask question=%r history_len=%d", request.question, len(history))
    try:
        return get_pipeline().ask(request.question, history=history)
    except Exception:
        logger.exception("/ask failed for question=%r", request.question)
        raise


@app.post("/ask/stream")
def ask_stream(request: AskRequest):
    history = [h.model_dump() for h in request.history]
    logger.info("POST /ask/stream question=%r history_len=%d", request.question, len(history))

    def event_generator():
        try:
            for event in get_pipeline().ask_stream(request.question, history=history):
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        except Exception:
            logger.exception("/ask/stream failed for question=%r", request.question)
            error_event = {"type": "error", "message": "發生錯誤，請稍後再試。"}
            yield f"data: {json.dumps(error_event, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
