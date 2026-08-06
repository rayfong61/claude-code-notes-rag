---
title: "Claude Code in Action - Routines and Headless"
source_url: "https://app.notion.com/p/3b3380860dab8042ad44d308e41b9985"
---

# Claude Code in Action - Routines and Headless

## 1. 核心概念：把重複工作交給 Claude

當你已經確認 Claude 能穩定完成某項任務，不要每天手動輸入 Prompt，改成自動化執行。Claude Code 自動化有一個光譜：Routines（低控制力）→ Headless Mode → Agent SDK（高控制力）。

## 2. Routines：雲端自動化任務

Routine = 儲存好的 Prompt + Repository + Connectors + Trigger。不需要自己架 Server、保持電腦開機、維護 Workflow Script，由 Anthropic Cloud 自動執行。

## 3. Routine 適合場景

適合「相同 Prompt + 定期觸發」，例如：
- **每日 Dependency Audit**：每天檢查 npm / pip package 是否有漏洞
- **PR Review Bot**：Trigger 為 GitHub Pull Request 建立，Claude 分析 code quality、找 bug、提出建議
- **Issue / Ticket 分析**：每天掃 Sentry Error，整理最高優先修復項目

## 4. Routine Trigger 類型

| Trigger | 例子 |
|---|---|
| Cron Schedule | 每天 9:00 執行 |
| HTTP POST | 自己的系統呼叫 API |
| GitHub Event | 新的 PR |

## 5. 建立 Routine 方法

- **方法 1：Web** — 進入 `claude.ai/code/routines`，設定名稱、Prompt、Repository、Trigger
- **方法 2：Claude Code** — Terminal 直接描述需求，例如 `/schedule daily dependency audit at 9am`

## 6. Routine 使用限制

1. **Research Preview**：Routine 目前仍是研究預覽功能，限制與行為可能改變
2. **Schedule 最快每小時一次**：可以每天 9:00，不能每 5 分鐘
3. **Repository 安全限制**：每次執行都是 fresh clone default branch，只能 push `claude/*` branch，避免 AI 直接修改 main

## 7. Headless Mode：程式控制 Claude

當 Routine 不夠用，需要自己環境、自己 Script、自己 Pipeline，使用 Headless Mode。核心：
```bash
claude -p "your prompt"
```
`-p` = `--print`，代表非互動模式。流程：Script → `claude -p` → Claude Output → 下一個 Pipeline。

## 8. Headless Mode 特點

它像一般 CLI 工具，Input 是 stdin，Output 是 stdout，所以可以組合成 pipeline：
```bash
command | claude -p | another_command
```
例如：
```bash
claude -p "summarize this diff"
```

## 9. Headless Mode 注意事項

重要：`-p` 不會自動載入 Hooks、Skills、Plugins、MCP Servers、CLAUDE.md。也就是說 `claude -p` = 乾淨環境啟動。優點是啟動快，缺點是不會繼承本地設定。

## 10. Structured Output（JSON）

Headless 常需要給程式處理，不要輸出一段文字，要輸出結構化 JSON。方法：指定 JSON Schema：
```bash
--output-format json
--json-schema '{}'
```
結果會包在 `structured_output` 欄位中，方便串接 `jq`、Database、Script。

## 11. Multi-step Automation（Session Resume）

複雜工作不用一次完成：
- **Step 1：產生計畫** — Claude 分析需求、建立 plan，保存 `session_id`
- **Step 2：恢復執行** — `claude --resume SESSION_ID`，Claude 會保留上一次對話、分析結果、工作狀態

適合 Plan → Execute 流程。

## 12. CI 使用：--bare

CI 最需要固定結果、可重現，使用 `--bare`，用途是 Pipeline、Automated testing、Build process，目的是避免每次結果不同。

## 13. Agent SDK：把 Claude 放進自己的 App

最高控制等級，架構：你的 Application → Agent SDK → Claude Code Engine，支援 TypeScript、Python。可以控制：
- `allowedTools`：限制 Claude 能做什麼（例如只給 `Read`、`Search`）
- system prompt：設定 Agent 行為
- permission mode：控制權限

## 14. Routines vs Headless vs Agent SDK

| 方式 | 適合 | 控制程度 |
|---|---|---|
| Routine | 固定重複工作 | 低 |
| Headless (-p) | 自己的 Script / Pipeline | 中 |
| --bare | CI 要固定結果 | 中高 |
| Agent SDK | 整合產品 | 最高 |

## 15. 實務選擇流程

- **每天自動檢查**（例如檢查 dependency）→ Routine
- **CI 自動產生 Report**（Git diff → Claude 分析 → 產生 JSON → 存 DB）→ Headless Mode
- **建立 AI Agent 產品**（AI Code Review SaaS、自動化工程平台）→ Agent SDK

## 最重要總結

- **Routines**：最簡單的自動化，設定一次，雲端定期執行
- **Headless**：Claude 變成 CLI 工具，你的 Script → `claude -p` → 自動流程
- **Agent SDK**：Claude 成為你的產品能力，App → Claude Agent → 使用者服務

對 AI Engineer 而言，推薦學習順序：Claude Code 基本操作 → Hooks 建立安全流程 → Headless + Script 自動化 → Agent SDK 開發 AI Agent 產品。
