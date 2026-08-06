---
title: "Claude Code in Action - Trust It: Verifying Unsupervised Runs"
source_url: "https://app.notion.com/p/3b3380860dab8066aae1e5c95c879ace"
---

# Claude Code in Action - Trust It: Verifying Unsupervised Runs

## 1. 核心概念：越少監督，越需要驗證

當 Claude 自主執行任務（Auto Mode 長時間執行、Headless Script、CI Pipeline、Overnight Agent Run），你沒有看到中間過程。信任 Claude 的關鍵不是相信，而是建立驗證機制。核心原則：監督越少，驗證越嚴格。

## 2. Unsupervised Run 使用 Auto Mode

建議使用 Auto Mode，不要用 Bypass Permissions。原因：Auto Mode 仍有 Classifier Model，會檢查危險 command、敏感操作、高風險行為。

但注意：**Auto Mode 不檢查 Code 正確性**，它只能判斷「這個操作危不危險」，不能判斷「這段 Code 有沒有 Bug」。例如 Claude 寫出 `def login(): return True`，安全模型可能允許，因為安全 ≠ 正確。

## 3. 驗證第一步：先看 Diff，不看 Summary

常見錯誤：直接看 Claude Summary（例如「Implemented authentication feature. Added tests. Improved security.」），看起來完美，但實際可能改錯檔案、改到不相關模組、刪除重要邏輯。

正確流程：
1. 執行 `/code-review`，讓 Claude 分析變更
2. 自己查看 `git diff`，確認改了哪些檔案、是否符合需求、是否有非預期修改

驗證原則：Summary = Claude 的說明；Diff = 真正發生的事情。真正可信的是 Diff。

## 4. Tests 要變成 Gate，不是 Promise

不要相信「Claude 說測試通過」，要讓系統強制驗證。

不好的流程：Claude 說「I ran tests, everything passed.」→ 直接相信。
好的流程：Claude 完成修改 → Hook 自動跑 Test → 成功才能結束。

## 5. 使用 Hooks 建立品質防線

**Stop Hook**：阻止 Claude 結束，如果測試失敗。流程：Claude 完成 → Stop Hook → pytest → Fail? → 不能停止。失敗時回傳 `exit 2`，Claude 收到「Fix the failing tests」的錯誤訊息，繼續修正。

## 6. Exit Code 很重要

- **Exit 0**：成功，允許繼續
- **Exit 2**：阻止並回傳錯誤，Claude 會看到 error message 與修正需求
- **Exit 1**：常見誤區，很多人以為會阻止，實際上只記錄錯誤，Claude 繼續

## 7. PostToolUse Hook

用途：每次修改後立即檢查。例如 Claude 修改 `src/auth.py`，PostToolUse 執行 `ruff check` 或 `npm run lint` 或 `tsc`。流程：Edit Code → PostToolUse → Lint / Type Check → 發現問題 → Claude 修正。

## 8. 使用 Cold Second Opinion（冷靜第二審）

讓沒有參與開發的 Agent Review。原 Claude 知道自己設計方向，可能忽略缺陷、合理化錯誤、假設太多；新的 Agent 沒有背景（Fresh Context），只看 Code、Diff、Requirement，更容易發現問題。流程：Agent A 負責開發 → Agent B 重新 Review → 發現問題。

## 9. Headless Run 驗證

對於 `claude -p` 自動化流程，不要只看文字輸出，要確認：
- **JSON Result**：例如 `{"status":"success","changes":...}`
- **Exit Code**：0 = 成功，非 0 = 失敗

## 10. 完整驗證流程

Claude Auto Run → 1. 查看 git diff → 2. `/code-review` → 3. Run Tests → 4. Stop Hook 驗證 → 5. Cold Agent Review → 6. Merge

## 11. 不同風險等級的驗證強度

| 情境 | 驗證程度 |
|---|---|
| 自己盯著 Claude 操作 | 快速 Review |
| Auto Mode 開發 | 看 Diff + Test |
| Headless Script | Diff + Test + Exit Code |
| CI 自動修改 | 完整 Hook + Second Review |
| Production 相關 | 人工審核 |

## 最重要總結

Claude 自動化的核心不是「放手」，而是「自主執行 + 自動驗證」。四個必做：
1. **看 Diff**：不要相信 Summary
2. **Test 變 Gate**：Hook 強制執行
3. **Exit Code 正確使用**：exit 2 = 阻止
4. **Cold Review**：讓另一個 Agent 用新視角檢查

最終可靠 Agent 架構：Permission Mode（控制 Claude 能做什麼）→ Hooks（控制 Claude 必須遵守什麼）→ Tests（確認結果正確）→ Second Review（降低盲點）。這才是讓 Claude 從「聊天工具」變成「可信任工程 Agent」的關鍵。
