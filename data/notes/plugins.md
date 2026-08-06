---
title: "Claude Code in Action - Plugins"
source_url: "https://app.notion.com/p/3b3380860dab80d1bcdddf8be7648f30"
---

# Claude Code in Action - Plugins

## 1. Plugin 是什麼？

Plugin 是 Claude Code 的可安裝套件，可將整個 `.claude` 環境打包分享。一個 Plugin 可包含：Skills、Subagents、Hooks、MCP Server 設定、Language Server (LSP)、Background Monitors、Themes、部分 `settings.json`。目的：不需要手動複製 `.claude` 資料夾，一次安裝即可。

## 2. 安裝 Plugin

```bash
/plugin install org-name@plugin-name
```
安裝完成後重新載入：`/reload-plugins`

## 3. Team 最佳做法：建立 Plugin Marketplace

如果團隊都有共用 Plugin，應建立私有 Marketplace：
```bash
/plugin marketplace add your-org/claude-plugins
```
好處：集中管理、Plugin 搜尋、自動版本管理、更新同步、不需每個人手動分享。之後安裝 Plugin 都會從 Marketplace 取得。

## 4. Plugin 安全性（最重要）

**Plugin 會以你的權限執行程式**。這代表 Hooks 會自動執行、MCP Server 可執行程式、Plugin 可以存取你的電腦。例如某個 Plugin 帶有 PreToolUse Hook 或 Stop Hook，它可能每次 Tool Call 都送資料到外部 API、寫入你的檔案、執行 Shell Command。

所以：不要因為想用 Skill 就直接安裝 Plugin，一定要先閱讀：有哪些 Hooks？有哪些 MCP Server？有哪些 Agents？有哪些 Commands？

## 5. Anthropic 的審核並不代表安全

Community Plugin 經過自動化審核，並非人工完整檢查。Official Marketplace 有官方維護，但 Reviewed ≠ Trusted。只安裝自己公司、自己團隊、自己信任的人發布的 Plugin。

## 6. Plugin 不會覆蓋你的設定

Plugin 與自己的設定會一起存在。例如你自己有 PreToolUse Hook，Plugin 也有 PreToolUse Hook，結果是兩個都會執行，而不是互相覆蓋。

## 7. Plugin Components 都有 Namespace

例如 Plugin `company-ai` 的 Skill `review-pr`，真正名稱會變成 `company-ai:review-pr`。因此不會撞名，可以安心共存。

## 8. Plugin 可以改變 Claude 行為

Plugin 可附帶 `settings.json`，但 Claude Code 只接受少數設定，其中最重要的是 `agent`。若指定 `agent = my-agent`，這個 Plugin 的 Subagent 可能直接成為 Main Agent、System Prompt、Tool 限制、Model 全部一起改變。也就是說：安裝 Plugin 後，Claude 的預設行為可能會改變。

## 9. Plugin 安裝後可管理

Plugin Panel 可查看 Plugin、查看內容、更新、移除。

## 10. 如何製作自己的 Plugin

其實不用改結構，直接把目前 `.claude` 打包即可：
```
.claude/
  skills/review/
  agents/reviewer.md
  hooks/hooks.json
  .mcp.json
```
Claude Code 會依照目錄自動發現 Skills、Agents、Hooks、MCP。

## 11. Plugin Manifest

位置：`.claude-plugin/plugin.json`
```json
{
  "name": "svg-splitter-review",
  "version": "0.1.0",
  "description": "...",
  "author": { "name": "Lewis Menelaws" }
}
```

重要欄位：
| 欄位 | 說明 |
|---|---|
| name | 唯一必填，作為 Namespace |
| version | 建議遵循語意化版本（Semantic Versioning），方便更新 |
| description | Plugin 說明 |
| author | 作者資訊 |

## 12. Manifest 可省略

即使沒有 `plugin.json`，Claude Code 仍然會依照 `skills/`、`agents/`、`hooks/` 自動找到所有元件。但若要分享、上 Marketplace、更新版本，仍建議建立 Manifest。

## 核心觀念（記住這兩件事）

- **使用 Plugin — Read Before Install**：安裝前一定檢查 Hooks、MCP Servers、Agents、Commands，因為 Plugin 會以你的權限執行。
- **開發 Plugin — Package Once It Works**：當 `.claude` 配置穩定後，打包成 Plugin，加上 `plugin.json`，放到 Marketplace，讓整個團隊只需一次安裝，即可共享相同的 Claude Code 工作環境。
