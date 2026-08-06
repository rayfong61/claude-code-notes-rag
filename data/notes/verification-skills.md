---
title: "Claude Code in Action - Verification Skills"
source_url: "https://app.notion.com/p/3b3380860dab8048868dc0e34e72374f"
---

# Claude Code in Action - Verification Skills

## 1. 為什麼第一個該建立 Verification Skill？

專案變大後，會一直重複做相同檢查：Refactor 完手動確認、修改功能手動跑測試、PR 前手動看 diff、Release 前手動檢查 checklist。問題：驗證流程依賴「人記得去做」，容易漏掉。

Verification Skill 的目的：讓 Claude 在完成工作後，自動執行固定驗證流程。例如要求 Claude「幫我重構這個 module」，完成後 Skill 自動觸發：執行測試 → 查看 git diff → 確認測試沒有被弱化 → 回報結果與證據。

## 2. 不只是測試通過，而是確認品質

很多人只做「修改 code → pytest → 全部 green → 完成」，但測試可能被偷偷改弱。例如原本 `assert result == expected_value` 被改成 `assert result is not None`，測試會過，但品質下降。

Verification Skill 要檢查：
- **Test Result**：測試是否通過、測試數量是否異常減少、coverage 是否下降
- **Diff Review**：修改是否符合需求、是否刪除重要邏輯、是否降低測試強度

真正完成定義：Done = 驗證流程執行 + 結果被確認，不是 Done = Claude 說完成。

## 3. Skill 不只是 skill.md

Skill 是一個資料夾：
```
.claude/skills/verification/
├── skill.md
├── reference.md
└── check.sh
```

- **skill.md**：保持簡短，負責 Skill 名稱、Trigger description、執行流程
- **reference.md**：放詳細規範（測試策略、code review checklist、安全規範、專案特殊要求），Claude 只有需要時才讀取，不用每次載入大量內容
- **scripts**：Skill 可以包含工具腳本（例如 `check.sh` 內容為 `pytest` / `git diff` / `coverage report`），Claude 執行 script 而不是把 script 內容讀進 context，優點是節省 token、流程一致、團隊共用

## 4. CLAUDE.md vs Skill vs Hook

| 類型 | 用途 | 例子 |
|---|---|---|
| CLAUDE.md | 永久規則 | coding convention |
| Skill | 任務流程 | release checklist |
| Hook | 強制執行 | 不允許跳過的檢查 |

- **CLAUDE.md** 適合「所有工作都適用」：使用 TypeScript、Component 使用 PascalCase、API 放 src/api、commit message 格式
- **Skill** 適合「特定任務流程」：例如 PR Review Skill（Run tests → Check diff → Check security issues → Generate review report）、Release Skill（Update version → Run test → Build → Generate changelog）
- **Hook** 適合「不能讓 Claude 跳過」：CLAUDE.md / Skill 是「Claude 會遵守」，Hook 是「程式一定執行」。例如禁止 `git commit` 除非 `pytest passed`，可用 git hook `pre-commit`

## 5. Skill 設計原則

- **Rule 1：重複兩次以上，就考慮 Skill**。例如你常常說「幫我跑測試、看 diff、確認 API 沒破壞」，就該建 Skill
- **Rule 2：skill.md 保持 Lean**。不要塞 5000 行規範，應該分層：簡單指令 → 詳細文件（reference.md）→ 自動化工具（scripts）

## 6. 最推薦建立的第一個 Skill：Verification Skill

原因：它改善所有其他工作。沒有它，Claude 修改後靠人檢查，可能忘記；有它，Claude 修改後自動跑 Verification Skill（Test → Diff → Report）。

## 7. 實際專案建議（適合 AI / Full Stack 開發）

FastAPI + React + AI Agent 專案可以建立：
```
.claude/skills/
├── verification/
│   ├── skill.md
│   ├── reference.md
│   └── verify.sh
├── api-review/
├── rag-evaluation/
└── deployment-check/
```

Verification Skill 可以檢查：
- **Backend**：pytest、FastAPI endpoint test、schema migration、API breaking change
- **Frontend**：npm test、lint、build
- **AI Application**：Prompt regression test、RAG retrieval accuracy、hallucination check、token cost

## 核心觀念一句話

CLAUDE.md 定義「平常怎麼做」，Skill 定義「特定事情怎麼做」，Hook 保證「一定會做」。而 Verification Skill 是最值得先建立的 Skill，因為它把「人工記得檢查」變成「流程自動驗證」。
