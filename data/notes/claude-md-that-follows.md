---
title: "Claude Code in Action - A CLAUDE.md That Follows"
source_url: "https://app.notion.com/p/3b3380860dab809d90cbc9e58d154361"
---

# Claude Code in Action - A CLAUDE.md That Follows

## 1. 核心觀念：CLAUDE.md 不是設定檔，而是「指導文件」

### 常見誤區
很多人會讓 CLAUDE.md 越寫越長：遇到問題就加一條規則，再遇到問題又加一條規則。最後變成文件過長、規則互相競爭、Claude 開始忽略部分內容。

原因：CLAUDE.md 的每一行都是「提示」，不是強制規則。Claude 會根據上下文權重理解，而不是像程式設定一樣 100% 執行。

### 原則
越精簡的 CLAUDE.md，Claude 越容易遵守。目標不是記錄所有事情，而是保留最重要的開發規範。

## 2. CLAUDE.md vs Hook

兩者用途不同：

| 類型 | CLAUDE.md | Hook |
|---|---|---|
| 性質 | 指導 | 強制執行 |
| Claude 是否可能忽略 | 可能 | 不可能 |
| 適合 | 開發習慣、風格 | 危險操作限制 |

判斷方式：問自己「如果 Claude 犯錯一次，我是否能接受？」
- 可以接受 → CLAUDE.md（例如使用 TypeScript、命名規則、API 結構）
- 不能接受 → Hook（例如不准刪 production database、不准 push main、不准修改 secret）

## 3. CLAUDE.md 的四個層級

Claude 可以讀取四種 CLAUDE.md，全部會一起載入：Managed Policy → User → Project → Local。

- **Managed Policy**：公司層級管理，使用者無法忽略（例如禁止提交 API Key）
- **User CLAUDE.md**（`~/.claude/CLAUDE.md`）：個人全域設定，跟隨所有專案
- **Project CLAUDE.md**（`project/CLAUDE.md`）：專案共享，團隊共同規範，通常會 commit 到 Git
- **Local CLAUDE.md**：個人專案備忘，只影響自己，不希望影響其他隊員

## 4. 大型 CLAUDE.md 使用 Import 拆分

當 CLAUDE.md 太大，改用 import：
```
CLAUDE.md
@.claude/conventions/code-style.md
@.claude/conventions/testing.md
@.claude/conventions/workflow.md
```
注意：Import 只是整理，不是減少 Context。Claude 啟動時會展開全部內容。好處是結構清楚、容易維護，但不會減少 token 或提升記憶容量。

## 5. 如何寫 Claude 容易遵守的規則？

**原則一：具體、可檢查**。避免「Follow best practices」這類抽象描述，改成「API routes must be placed in `src/api/handlers/`，one route per file」這種可檢查的規則。

**原則二：不只禁止，要提供替代方案**。規則公式：不要做 A + 請做 B。例如不要寫「不要使用 default export」，要寫「Use named exports instead of default exports」。

**原則三：不要濫用 IMPORTANT / MUST**。強調詞是有限資源，大量使用會讓所有規則權重相同，最後沒有任何規則突出。建議只保留 2~3 個最高優先級。

## 6. CLAUDE.md 要像程式碼一樣維護

不要把它當文件，應該像 production code 持續改善。當 Claude 犯錯時：分析原因 → 新增規則 → 更新 CLAUDE.md → 下次避免。甚至可以直接要求 Claude 幫忙把這次的錯誤預防規則加進 CLAUDE.md。

## 7. CLAUDE.md 最佳結構範例

```
# Project Overview
簡短介紹專案

# Tech Stack
React / FastAPI / PostgreSQL

# Coding Rules
- Use named exports
- One API route per file

# Testing
- Run pytest before commit

# Workflow
- Create feature branch
- Write tests first
```
保持短、明確、可驗證。

## 最重要的五個 Takeaways

1. 越短越好：長文件降低遵守率
2. 危險規則用 Hook：CLAUDE.md 不是安全機制
3. 使用 Import 管理：組織，不是減少 Context
4. 規則要具體：避免抽象描述
5. 持續更新：Claude 犯錯就是改善機會

## 一句話總結

CLAUDE.md 不是寫給 Claude「記住所有事情」，而是提供少量、高價值、可驗證的開發指引；真正不能犯錯的事情交給 Hook 強制控制。
