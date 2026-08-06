"""Headless-friendly entry point to rebuild the RAG index from data/notes/.

Usage:
    python scripts/reindex.py

Or via Claude Code headless mode (Routines and Headless practice):
    claude -p "Re-run ingestion on data/notes and rebuild the index" \
        --allowedTools "Bash(python scripts/reindex.py)"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.ingest import main

if __name__ == "__main__":
    main()
