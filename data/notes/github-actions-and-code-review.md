---
title: "Claude Code in Action - GitHub Actions and Code Review"
source_url: "https://app.notion.com/p/3b3380860dab80f29e35fcb094e51adf"
---

# Claude Code in Action - GitHub Actions and Code Review

## 1. 核心概念

Pull Request（PR）是最適合導入 AI 自動化的位置，因為 Code Review 發生在這裡、Code 合併在這裡、大量重複工作集中在這裡。Claude 提供兩種方式：Code Review（Managed Service，單純 AI 審查 PR）與 GitHub Action（自訂 CI/CD 自動化）。

## 2. Code Review（Anthropic Managed Service）

Anthropic 提供的託管服務，不需要自己寫 Workflow、不需要維護 Server，Claude GitHub App 自動審查 PR。流程：Developer Push Code → Pull Request → Claude Review Agent → Inline Comments。

## 3. Code Review 啟用方式

需要 Organization Admin，在 Claude Code Admin Settings → Code Review → Configure 設定，接著安裝 Claude GitHub App、選擇 Repository、設定觸發方式。

## 4. Code Review Trigger

| Trigger | 說明 |
|---|---|
| PR Open | PR 建立時檢查一次 |
| Every Push | 每次更新 PR 都檢查 |
| @claude review | 人工要求 Claude Review |

## 5. Code Review 如何工作

Claude 不只看修改檔，會結合 PR Diff + 完整 Codebase Context 分析問題，產生 Inline Comment，輸出包含問題位置、Severity 等級、問題說明、建議修正方式。例如：「Line 42, Potential SQL Injection, Suggested fix: Use parameterized query」。

## 6. Code Review 優點：自動去重與排序

避免出現 100 個小問題淹沒重點，Claude 會 deduplicate、rank findings，變成 5 個真正重要問題。

## 7. Code Review 限制

- **不會 Approve PR**：Claude 只發現問題，人決定是否 Merge
- **不會自動修正**：Managed Code Review 只會 Comment，不會 Commit Fix
- **目前狀態**：Research Preview，僅 Team Plan / Enterprise Plan，功能可能變動

## 8. 如何套用 Code Review 修正

流程：Claude Review 找到問題 → Pull Code 到 Local → 執行 `/code-review --fix` → 修改 Working Tree。

## 9. GitHub Action（自行控制）

當需求超過 Code Review，使用 `anthropics/claude-code-action@v1`，適合自動修改程式、回應 PR Comment、Scheduled Report、自訂 CI Workflow。

## 10. GitHub Action Setup

Claude Code 執行 `/install-github-app`，需要 Repository Admin 權限與 Anthropic API Key Secret。

## 11. GitHub Action 常用參數

| 參數 | 用途 |
|---|---|
| anthropic_api_key | Anthropic API Key |
| github_token | GitHub Token |
| trigger_phrase | 觸發文字 |
| prompt | Claude 指令 |
| claude_args | Claude CLI 參數 |
| use_bedrock | AWS Bedrock |
| use_vertex | Google Vertex |

## 12. PR Comment 觸發 Claude

Workflow 檔案 `.github/workflows/claude.yaml`：
```yaml
- uses: anthropics/claude-code-action@v1
  with:
    anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
    github_token: ${{ secrets.GITHUB_TOKEN }}
    trigger_phrase: "@claude"
    prompt: "Your instructions here"
    claude_args: "--max-turns 5"
```
流程：Developer 留言 `@claude implement this feature` → GitHub Action → Claude 修改 code、Push commit、留下執行摘要。

## 13. Scheduled Automation

GitHub Action 不只 PR，也可以用 cron schedule（例如每天 09:00 UTC 執行 Dependency report、Bug scan、Code quality report），也可以用 `workflow_dispatch` 手動觸發。

## 14. claude_args 調整

- `--max-turns 5`：限制 Agent Loop，避免 Claude 無限執行
- **Permission Mode**：無人值守時不要等待人工確認，需要允許自動執行
- **Allowed Tools**：最小權限原則，例如 Report 任務只給 `Read`、`Search`，不要給 `Deploy`、`Delete`

## 15. Code Review vs GitHub Action 比較

| | Code Review | GitHub Action |
|---|---|---|
| 目的 | Review PR | 執行自動化任務 |
| 設定難度 | 低 | 中 |
| 是否寫 Workflow | 否 | 是 |
| 是否修改 Code | 否 | 是 |
| 是否 Commit | 否 | 是 |
| 適合 | Reviewer | Developer Automation |

## 16. 選擇策略

- 需求是「AI 幫忙看 PR」→ 使用 Code Review（Claude 找問題 → 人修正）
- 需求是「AI 幫忙完成工作」→ 使用 GitHub Action（`@claude implement feature` → Claude 修改 code → Push commit）

## 17. 建議導入順序

Step 1：開啟 Code Review，建立 AI PR Reviewer。Step 2：加入 GitHub Action，自動處理固定任務。Step 3：加入 Scheduled Agent，每日品質檢查。

## 最重要總結

- **Code Review**：Claude 是你的 AI Reviewer（PR → Claude 找問題 → Human 決策）
- **GitHub Action**：Claude 是你的 AI Developer（Event → Claude Agent → 修改/Commit/Report）

判斷原則：只需要評論？→ Code Review；需要 Claude 動手做？→ GitHub Action。對 AI 工程團隊而言，最佳架構通常是 GitHub PR 同時搭配 Claude Code Review（找問題）與 GitHub Action（自動修復/自動化流程），形成完整 AI 輔助開發流程。
