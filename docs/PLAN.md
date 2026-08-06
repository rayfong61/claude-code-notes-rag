# 文件 RAG 問答系統 — 作品集專案 + Claude Code in Action 練習計畫

## Context

使用者正在準備 AI 應用工程師的作品集，想在一個下午內做出一個可展示的 RAG（Retrieval-Augmented Generation）問答系統。同時，使用者這幾天在 Notion 記錄了一系列「Claude Code in Action」教學筆記（CLAUDE.md、Permission Modes、Verification Skills、Hooks、Plugins、Routines and Headless、GitHub Actions and Code Review、Steering Long Sessions、Trust It），希望能透過實際打造這個專案，把九篇筆記的技巧都動手練過一輪，而不是只停留在筆記閱讀。

**兩個目標同時達成的策略**：把這九個 Claude Code 技巧當作「怎麼開發這個專案」的方法論，自然地嵌入到開發流程的每個階段裡（例如：開工前先寫 CLAUDE.md、用 Hooks 自動跑測試、用 headless 模式跑索引重建、用 goal 讓 Claude 自主完成一段功能），而不是做完 app 後再另外補做九個不相干的練習。

語料庫直接使用使用者自己的「Claude Code in Action」9 篇 Notion 筆記內容（已透過 Notion MCP 連接取得），這樣示範的問答內容對使用者自己也有意義，且不需額外尋找文件素材。

技術選擇（已與使用者確認）：
- 檢索 embedding：**Voyage AI**（Anthropic 官方推薦的 embedding 供應商，`voyage-3-lite` 模型，需另外申請 [voyageai.com](https://voyageai.com) 的 API key，有免費額度）
- 生成：Anthropic Claude API（使用者已有 API key）
- 兩把 API key 都要放在 `.env`（gitignore），與 Claude Code 訂閱本身無關

## Tech Stack

| 項目 | 選擇 | 原因 |
|---|---|---|
| 語言 | Python 3.12（已安裝） | 符合使用者近期 FastAPI/後端練習方向 |
| API 框架 | FastAPI + uvicorn | 輕量、自帶 OpenAPI 文件，適合展示 |
| Embedding | Voyage AI (`voyageai` SDK, `voyage-3-lite`) | Anthropic 官方推薦，作品集加分，純 API 呼叫不需下載大型模型 |
| 向量儲存 | 純 Python + numpy，存成本地 `data/index.json`（向量+文字+metadata） | 語料庫僅 9 篇筆記，規模小，不需要 chromadb 等額外服務，架構單純好講解；README 會註明「正式環境可換成 pgvector/Chroma」 |
| 生成 | Anthropic Claude API (`anthropic` SDK, 建議 `claude-sonnet` 系列) | 展示 RAG 的生成端 + 引用來源 |
| 前端 | 單一 `index.html` + vanilla JS（fetch API） | 不需建置流程，一個下午內可完成，仍可展示問答互動與來源引用 |
| 測試 | pytest | 供 Hooks / Verification Skills 練習掛載 |

## 專案結構

```
learn_claude_code/
├── CLAUDE.md                  # 專案規範（Phase 0 練習：CLAUDE.md That Follows）
├── .claude/
│   └── settings.json          # 權限模式 + Hooks 設定（Phase 1, 5 練習）
├── data/
│   ├── notes/                 # 9 篇筆記匯出成 .md（RAG 語料庫）
│   └── index.json             # ingest.py 產出的向量索引
├── backend/
│   ├── requirements.txt
│   ├── ingest.py               # 讀 data/notes → chunk → Voyage embed → 存 index.json
│   ├── store.py                 # 讀寫 index.json，cosine similarity 檢索
│   ├── rag.py                   # 組 prompt（含檢索片段）→ 呼叫 Claude → 回答+引用
│   └── main.py                  # FastAPI app，POST /ask、GET /health
├── frontend/
│   └── index.html               # 簡易問答介面，call /ask
├── tests/
│   └── test_rag.py              # pytest：檢索正確性 + /ask smoke test
├── scripts/
│   └── reindex.py               # 可被 headless 模式呼叫的重建索引指令
├── .env.example
└── README.md                    # 專案說明 + 使用的 Claude Code 技巧總覽（作品集加分項）
```

## 開發階段（對應九篇筆記的練習）

**Phase 0 — CLAUDE.md That Follows**
在寫任何程式碼之前，先寫根目錄 `CLAUDE.md`：說明專案目的、技術棧、開發慣例（例如「改完 backend 程式碼一定要跑 `pytest` 才算完成」「`.env` 絕不能被讀出或提交」「chunk 大小、檢索 top-k 等慣例」）。

**Phase 1 — Permission Modes**
建立 `.claude/settings.json`，針對這個 Python 專案設定合理的 `allow` 清單（例如 `Bash(python:*)`、`Bash(pytest:*)`、`Bash(uvicorn:*)`），示範怎麼替專案客製權限模式，減少開發過程中的重複確認。

**Phase 2 — Routines and Headless**
1. 用已連接的 Notion MCP 工具把剩下 8 篇筆記（Steering Long Sessions 已抓過）內容 fetch 下來，存成 `data/notes/*.md`。
2. 寫 `backend/ingest.py`（chunk by heading → Voyage embed → 存 `data/index.json`）與 `scripts/reindex.py`。
3. 示範用 headless 模式重建索引：`claude -p "重新掃描 data/notes 並重建索引" --allowedTools "Bash(python:*)"`，對應「Routines and Headless」筆記中 CI/自動化情境的用法。

**Phase 3 — Steering Long Sessions（實際運用，非只讀筆記）**
開發 `backend/store.py`（cosine similarity top-k 檢索）、`backend/rag.py`（組 prompt + 呼叫 Claude + 回傳引用來源）、`backend/main.py`（FastAPI `/ask`、`/health`）。這是最長的一段實作，會實際使用：
- `/goal` 設定完成條件（例如「`/ask` 能對測試問題回傳含引用來源的答案，且 pytest 全過」）
- 需要時用 `/compact` 聚焦、`/rewind` 導正方向

**Phase 4 — Verification Skills + Trust It: Verifying Unsupervised Runs**
- 寫 `tests/test_rag.py`：檢索正確性測試（問 Hooks 相關問題應檢索到 Hooks 那篇筆記片段）、`/ask` smoke test。
- 建立一個 verification skill / 在 CLAUDE.md 中明訂「完成任何後端改動前必跑 pytest」的驗證流程。
- 實際示範「Trust It」：給 Claude 一個範圍明確的小任務（例如「幫 `/ask` 加上回傳來源筆記標題與連結」），讓它自主執行，僅在驗證失敗時介入，而不是逐步盯著看。

**Phase 5 — Hooks**
在 `.claude/settings.json` 加一個真正的 hook：`PostToolUse` 監聽對 `backend/*.py` 的 Edit/Write，自動跑 `pytest -q`，測試失敗時提示。與 Phase 4 的 verification skill 互補（Hooks = 事件觸發的固定腳本；Verification Skills = 指引 Claude 主動執行的驗證流程）。

**Phase 6 — 前端**
`frontend/index.html`：輸入問題 → 呼叫 `/ask` → 顯示回答與引用的筆記來源（含 Notion 連結）。無框架、無建置步驟。

**Phase 7 — Plugins（stretch，視剩餘時間）**
若時間允許，瀏覽並安裝一個現有的 Claude Code plugin（例如 lint 或 doc 相關），完成九篇筆記中最後一項的實際操作；非必要不影響主專案完成度。

**Phase 8 — GitHub Actions and Code Review（stretch，需另外確認）**
此專案目前在本機 git repo（無 remote）。若使用者之後想推到 GitHub 並串接 `/install-github-app` + PR 自動 code review workflow，屬於「推送到共享環境」的動作，會另外向使用者確認是否要建立 GitHub repo 並 push，不在本次無人確認下自動執行。

**Phase 9 — README 收尾**
撰寫 `README.md`：專案說明、架構圖（文字即可）、如何啟動、以及「開發過程中使用的 Claude Code 技巧」對照表 —— 這份對照表本身也是作品集加分項，展現 AI 輔助工程的方法論，不只是最終產出的 app。

## 需要使用者提供

- `.env` 中的 `ANTHROPIC_API_KEY`（已具備）與 `VOYAGE_API_KEY`（需至 voyageai.com 申請，有免費額度）

## 驗證方式（end-to-end）

1. `pip install -r backend/requirements.txt`
2. 設定 `.env`（`ANTHROPIC_API_KEY`、`VOYAGE_API_KEY`）
3. `python backend/ingest.py` → 產出 `data/index.json`
4. `pytest -q` → 單元測試全過
5. `uvicorn backend.main:app --reload` → 啟動伺服器，`http://localhost:8000/docs` 確認 API 正常
6. 開啟 `frontend/index.html`，輸入例如「Claude Code 的 Hooks 是什麼？」，確認回答內容正確且附上引用來源（對應到 Hooks 那篇筆記）
