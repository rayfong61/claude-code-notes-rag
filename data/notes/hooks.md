---
title: "Claude Code in Action - Hooks"
source_url: "https://app.notion.com/p/3b3380860dab804ba7cdf8993d3a4b02"
---

# Claude Code in Action - Hooks

## 1. Hooks 的核心概念

CLAUDE.md：「告訴 Claude 應該做什麼」，但它只是建議（request），Claude 通常會遵守，但不是 100%。

Hook：「強制 Claude 一定執行某個行為」，它是 deterministic code（固定執行程式），在指定時間點觸發，可以阻止、修改、驗證 Claude 行為。概念：CLAUDE.md = 希望 Claude 做；Hook = Claude 不可能跳過。

## 2. Hook 在 Agent Loop 的位置

Claude Code 一次工作流程：Session Start → User Prompt → Claude Thinking → Tool Call → Tool Result → Turn End → Compact。Hooks 可以插入這些節點。

## 3. 最重要的 Hook Events

Claude Code 約有 30 種 Hook Events，實務最常用：

| Hook | 時機 | 用途 |
|---|---|---|
| **PreToolUse** | Tool 執行前 | 阻止危險操作、修改指令 |
| **PostToolUse** | Tool 成功後 | Formatter、Lint |
| **Stop** | Claude 想結束時 | 強制驗證完成條件 |
| **SubagentStop** | 子 Agent 結束 | 驗證子任務 |
| **SessionStart** | Session 開始 | 初始化環境、恢復狀態 |
| **PreCompact** | Compact 前 | 保存資訊 |
| **PostCompact** | Compact 後 | 通常較少使用 |
| **InstructionsLoaded** | CLAUDE.md 載入 | 檢查 context |

## 4. 三個最重要 Hook

### (1) PreToolUse
最強大的 Guardrail。流程：Claude 準備呼叫工具 → PreToolUse → 允許/阻止/修改 → 真正執行。用途：禁止危險 command、防止 secret 外洩、限制 production 操作。

PreToolUse 回傳 JSON 格式：
```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Dangerous command"
  }
}
```
`permissionDecision` 三種值：`allow`（允許執行）、`deny`（阻止）、`ask`（交給使用者決定）。

**updatedInput：修改 Claude 指令**。PreToolUse 不只能阻擋，也可以修改輸入後再執行。例如 Claude 執行的指令帶有 `sk_live_xxxxx` 這類 secret，Hook 發現後可以修改成 `REDACTED`，結果是原工作完成、Secret 沒有外洩。

### (2) PostToolUse
執行後觸發，適合自動格式化（例如 `prettier --write .`）或自動檢查（例如 `npm run lint`、`pytest`）。注意：PostToolUse 太晚，因為 Tool 已經執行完才觸發，不能阻止危險操作。

### (3) Stop Hook
控制 Claude 是否可以結束。流程：Claude 說「完成了」→ Stop Hook → 檢查測試通過？build 成功？文件更新？→ 允許停止 / 要求繼續。用途：建立「Claude 不完成不能停」，例如要求完成 API 後必須通過 pytest。

## 5. SessionStart Hook

最重要用途：Compact 後恢復 Context。很多人誤用 PostCompact，正確做法是 SessionStart + compact matcher。流程：長對話 → Compact → SessionStart Hook → 輸出工作摘要 → Claude 恢復狀態。例如輸出目前工作進度（Editing auth module、Added JWT middleware、Pending: write tests），Claude 不會忘記進度。

## 6. Hook Exit Codes

如果 Hook 不使用 JSON，靠 exit code 控制：
- **Exit 0**：成功，Allow，正常完成
- **Exit 2**：阻擋，Block（例如禁止 `rm -rf /`）
- **Exit 其他值**：非阻擋錯誤，Claude 繼續執行

常見陷阱：很多人以為 `exit 1` = block，這是錯的。實際 `exit 1` = error log，Claude 繼續。要阻擋必須用 `exit 2`。

## 7. Auto Mode + Hooks = 完整 Agent 安全模型

Permission Modes 的 Auto Mode 只靠 Classifier 判斷危險，不能判斷程式品質。加入 Hooks 後：Auto Mode 防止危險操作（PreToolUse）+ 驗證結果（Stop Hook），形成 Intent Safety + Correctness Verification 的完整組合。

## 8. 實務推薦配置（AI Engineer）

- **日常開發**：Accept Edits + PostToolUse（自動 prettier、eslint、pytest）
- **長時間 Agent 任務**：Auto Mode + PreToolUse（防止危險 command）+ Stop Hook（確認 test 通過）
- **CI / 無人值守**：Don't Ask + Hooks

## 最重要總結

Hooks 的價值：把「Claude 通常會遵守」提升成「Claude 一定遵守」。三個最值得建立的 Hook：
1. **PreToolUse**：防止錯誤或危險行為（禁止 rm、防 secret 外洩、限制 deploy）
2. **PostToolUse**：自動維護品質（formatter、lint）
3. **Stop**：確保 Claude 真的完成（test 通過、build 成功）

對 AI Agent 開發來說：Permission Mode 控制「能不能做」，Hook 控制「應不應該做」，Test 控制「做得對不對」。三者組合才是可靠的 Claude Code 自動化流程。
