# Claude Code Notes RAG

一個文件問答系統（RAG，Retrieval-Augmented Generation）：語料庫是「Claude Code in Action」9 篇學習筆記，使用者可以用自然語言提問，系統會檢索相關筆記片段，並用 Claude 生成附引用來源的回答。

這個專案同時也是實際練習 Claude Code 開發流程的紀錄——見下方[開發過程中使用的 Claude Code 技巧](#開發過程中使用的-claude-code-技巧)。

## 架構

```
問題
  ↓
Voyage AI 把問題轉成向量（voyage-3-lite）
  ↓
cosine similarity 在 data/index.json 找出最相關的筆記片段
  ↓
把片段 + 問題組成 prompt
  ↓
Claude API 生成回答（附引用來源）
  ↓
回答 + 來源連結
```

技術棧：Python 3.12 + FastAPI（後端）、Voyage AI（embedding）、Anthropic Claude API（生成）、純 numpy 向量儲存（無額外向量資料庫）、vanilla HTML/JS（前端）。

## 專案結構

```
CLAUDE.md              專案開發規範
docs/PLAN.md            完整開發計畫
data/notes/*.md         語料庫（9 篇 Claude Code in Action 筆記）
data/index.json         ingest.py 產出的向量索引（不進版控，需自行產生）
backend/ingest.py       chunk + embed 筆記，建立索引
backend/store.py        cosine similarity 向量檢索
backend/rag.py           檢索 + 組 prompt + 呼叫 Claude 生成回答
backend/main.py          FastAPI app（/ask、/ask/stream、/health）
frontend/index.html      問答介面
tests/test_rag.py        pytest：chunking、檢索排序、/ask smoke test
scripts/reindex.py        headless 模式可呼叫的重建索引指令
.claude/settings.json     權限模式 + PostToolUse Hook（自動跑測試）
.claude/skills/verification/  Verification Skill
```

## 啟動方式

1. 安裝套件：
   ```bash
   pip install -r backend/requirements.txt
   ```
2. 設定 `.env`（複製 `.env.example`）：
   ```
   ANTHROPIC_API_KEY=...
   VOYAGE_API_KEY=...
   ```
   Voyage AI key 需至 [voyageai.com](https://voyageai.com) 申請（有免費額度）。
3. 建立向量索引：
   ```bash
   python backend/ingest.py
   ```
4. 跑測試：
   ```bash
   pytest -q
   ```
5. 啟動後端：
   ```bash
   uvicorn backend.main:app --reload
   ```
6. 開啟 `frontend/index.html`（直接用瀏覽器開檔案即可，無需建置），輸入問題，例如「Claude Code 的 Hooks 是什麼？」。

## 開發過程中使用的 Claude Code 技巧

這個專案本身也是實際動手練習「Claude Code in Action」九篇筆記的紀錄：

| 筆記 | 在這個專案裡怎麼用 |
|---|---|
| A CLAUDE.md That Follows | 開工前先寫 `CLAUDE.md`，界定技術棧與開發慣例（測試必過、`.env` 保密、chunk 規則），後續又用 `/init` 補強成含常用指令、架構說明的完整版 |
| Permission Modes | `.claude/settings.json` 針對 Python 專案客製 `allow` 清單，減少重複確認 |
| Routines and Headless | `scripts/reindex.py` 設計成可被 `claude -p` headless 模式呼叫，重建向量索引 |
| Steering Long Sessions | 開發 RAG 後端核心、多輪對話與 streaming 功能時用 Plan Mode 先界定範圍，再逐步實作 |
| Verification Skills | `.claude/skills/verification/` 定義「改完程式碼要跑測試、看 diff」的固定驗證流程 |
| Hooks | `.claude/settings.json` 加入 `PostToolUse` hook，Edit/Write 後自動跑 `pytest -q`；實際遇過一次真實的 rate-limit 失敗被 hook 擋下，驗證了它會真的阻擋、不是紙上談兵 |
| Trust It: Verifying Unsupervised Runs | 每個 Phase 完成後實際執行 `pytest` 與 API smoke test（例如用 curl 驗證 SSE streaming 輸出）驗證，而非只看 Claude 的文字摘要 |
| Plugins | 尚未實際安裝/使用 plugin，留待後續練習 |
| GitHub Actions and Code Review | Repo 已建立並 push 到 [rayfong61/claude-code-notes-rag](https://github.com/rayfong61/claude-code-notes-rag)，但尚未設定 CI workflow 或 PR 自動 code review，留待後續練習 |

完整計畫見 [`docs/PLAN.md`](docs/PLAN.md)。
