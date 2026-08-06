# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 專案：Claude Code Notes RAG

文件問答系統（RAG）。語料庫是 `data/notes/` 底下的 Markdown 筆記（匯出自 Notion 的「Claude Code in Action」系列），使用者可以用自然語言提問，系統會檢索相關筆記片段並用 Claude 生成附引用來源的回答。這個專案同時也是練習 Claude Code 開發流程（CLAUDE.md、Permission Modes、Hooks、Headless、Verification 等）的沙盒，詳見 `docs/PLAN.md`。

## 技術棧

- Python 3.12 + FastAPI + uvicorn
- Embedding：Voyage AI（`voyageai` SDK，`voyage-3-lite`）
- 生成：Anthropic Claude API（`anthropic` SDK，`claude-sonnet-4-5`）
- 向量儲存：純 Python + numpy，存成 `data/index.json`（規模小，不用額外的向量資料庫）
- 前端：單一 `frontend/index.html`，vanilla JS，無建置步驟
- 測試：pytest

## 常用指令

```bash
pip install -r backend/requirements.txt   # 安裝依賴
python backend/ingest.py                  # 重建向量索引（或 python scripts/reindex.py）
pytest -q                                 # 跑全部測試
pytest -q tests/test_rag.py::test_chunk_by_heading_splits_on_level_two_headings  # 跑單一測試
uvicorn backend.main:app --reload         # 啟動後端（http://localhost:8000/docs）
```

`.env`（複製自 `.env.example`）需設定 `ANTHROPIC_API_KEY` 與 `VOYAGE_API_KEY`。前端直接用瀏覽器開 `frontend/index.html` 即可，call 本機後端 API，無需建置。

`tests/test_rag.py` 中會打真正 API 的測試（`test_ask_endpoint_returns_cited_answer`）在缺少 API key 時會自動 skip，其餘測試（chunking、檢索排序、pipeline 邏輯）用 fake client，離線可跑。

## 架構

單一資料流向的 RAG pipeline，沒有分支邏輯：

```
問題 → Voyage embed（query） → VectorStore cosine similarity 找 top-k 片段
     → 組成 prompt（片段 + 對話歷史） → Claude 生成回答 → 回答 + 引用來源
```

- `backend/ingest.py`：離線建索引流程。讀 `data/notes/*.md` → 解析 frontmatter（`title`、`source_url`）→ `chunk_by_heading` 依 `##` 標題切片（每片保留 `#` 主標題）→ Voyage embed → 寫入 `data/index.json`。這是唯一寫入索引的地方，索引檔本身不手動編輯。
- `backend/store.py`：`VectorStore` 載入 `data/index.json`，把 embedding 正規化後用 cosine similarity 做 top-k 檢索，純 numpy 運算，無外部向量資料庫。
- `backend/rag.py`：`RagPipeline.ask()` 是核心入口——embed 問題、呼叫 `VectorStore.search`、組 context prompt、呼叫 Claude、整理去重後的來源清單一併回傳。支援多輪對話（`history` 參數會原樣併入 messages）。
- `backend/main.py`：FastAPI app，僅兩個路由：`GET /health`、`POST /ask`（body 含 `question` 與可選 `history`）。`RagPipeline` 用 module-level 單例（`get_pipeline()`）延遲初始化，避免每個 request 重新建立 API client。
- `scripts/reindex.py`：`backend/ingest.py:main` 的 headless 友善入口，供 `claude -p` 或 CI 呼叫重建索引。
- `data/notes/*.md`：每篇筆記檔頭需有 `title`/`source_url` frontmatter（見任一現有檔案），供 `backend/rag.py` 生成引用來源時使用。

## 開發慣例

- 改動 `backend/` 下的程式碼後，一定要跑 `pytest -q` 全過才算完成，不要略過測試就宣告完工（`.claude/skills/verification/` 定義了完整驗證流程，`.claude/settings.json` 也設了 PostToolUse hook 在 Edit/Write 後自動跑）。
- `.env`（含 `ANTHROPIC_API_KEY`、`VOYAGE_API_KEY`）絕不能被讀出、印出、或提交進 git。範例格式放在 `.env.example`。
- 新增或修改 `data/notes/` 內容後，需重新跑 `python backend/ingest.py`（或 `scripts/reindex.py`）重建 `data/index.json`，索引檔不手動編輯。
- 檢索片段（chunk）以 Markdown 標題（`#`/`##`）為邊界切分，不要用固定字數硬切，避免切斷語意。
- `backend/rag.py` 產生回答時必須附上引用來源（筆記標題 + 對應的 Notion URL），不要生成沒有來源依據的內容。
- 專案規模小，優先維持架構單純（例如向量儲存不上 chromadb），不要為了展示技術而過度工程化。
- 不要在 `.env`、`data/index.json` 之外新增其他機密或大型產出物到 git 版控。
