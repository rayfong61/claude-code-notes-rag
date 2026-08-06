# 專案：Claude Code Notes RAG

文件問答系統（RAG）。語料庫是 `data/notes/` 底下的 Markdown 筆記（匯出自 Notion 的「Claude Code in Action」系列），使用者可以用自然語言提問，系統會檢索相關筆記片段並用 Claude 生成附引用來源的回答。這個專案同時也是練習 Claude Code 開發流程（CLAUDE.md、Permission Modes、Hooks、Headless、Verification 等）的沙盒，詳見 `docs/PLAN.md`。

## 技術棧

- Python 3.12 + FastAPI + uvicorn
- Embedding：Voyage AI（`voyageai` SDK，`voyage-3-lite`）
- 生成：Anthropic Claude API（`anthropic` SDK）
- 向量儲存：純 Python + numpy，存成 `data/index.json`（規模小，不用額外的向量資料庫）
- 前端：單一 `frontend/index.html`，vanilla JS，無建置步驟
- 測試：pytest

## 開發慣例

- 改動 `backend/` 下的程式碼後，一定要跑 `pytest -q` 全過才算完成，不要略過測試就宣告完工。
- `.env`（含 `ANTHROPIC_API_KEY`、`VOYAGE_API_KEY`）絕不能被讀出、印出、或提交進 git。範例格式放在 `.env.example`。
- 新增或修改 `data/notes/` 內容後，需重新跑 `python backend/ingest.py`（或 `scripts/reindex.py`）重建 `data/index.json`，索引檔不手動編輯。
- 檢索片段（chunk）以 Markdown 標題（`#`/`##`）為邊界切分，不要用固定字數硬切，避免切斷語意。
- `backend/rag.py` 產生回答時必須附上引用來源（筆記標題 + 對應的 Notion URL），不要生成沒有來源依據的內容。
- 專案規模小，優先維持架構單純（例如向量儲存不上 chromadb），不要為了展示技術而過度工程化。
- 不要在 `.env`、`data/index.json` 之外新增其他機密或大型產出物到 git 版控。
