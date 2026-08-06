---
title: "Claude Code in Action - Permission Modes"
source_url: "https://app.notion.com/p/3b3380860dab8038bb07d41d352dcc53"
---

# Claude Code in Action - Permission Modes

## 1. Permission Modes 的目的

Permission Modes 用來控制 Claude 可以自動執行哪些操作，避免每個指令都需要人工確認。核心概念：根據任務風險，選擇適合的信任等級，讓 Claude 自動化工作。

## 六種 Permission Modes

| Mode | Claude 可以做什麼 | 適用情境 |
|---|---|---|
| **Manual** | 只能讀取，自動操作以外都需詢問 | 最安全，探索陌生專案 |
| **Accept Edits** | 可讀取、修改檔案、執行常見檔案系統操作 | 日常開發、快速迭代 |
| **Plan** | 只能讀取與分析，不修改 | 架構設計、需求分析 |
| **Auto** | 自動執行，多數操作由安全模型檢查 | 長時間自主開發 |
| **Don't Ask** | 只允許事先白名單工具，其餘直接拒絕 | CI/CD、自動任務 |
| **Bypass Permissions** | 跳過所有安全檢查 | 僅限隔離環境 |

日常使用可按 `Shift + Tab` 循環切換：Manual → Accept Edits → Plan → Auto。底部 Status Bar 會顯示目前模式。

## Auto Mode（最重要）

Auto = Claude Code 的「半自主模式」。流程：你的需求 → Claude 執行操作 → Classifier Model 檢查意圖 → 允許/阻擋 → 執行。

**Auto Mode 會阻擋高風險操作**，例如：production deploy、database migration、force push（`git push --force`）、直接執行下載程式（`curl xxx | bash`）、傳送敏感資料到外部 API、刪除重要 session 檔案。

**Auto Mode 會允許一般開發操作**，例如：修改本地程式碼、安裝 lock file 定義的 dependency（`npm install`、`pip install -r requirements.txt`）、查詢資料、push 自己的 branch。

## Auto Mode 的限制

重要觀念：Classifier 檢查「危險性」，不是「正確性」。它不能判斷程式是否有 bug、架構是否最佳、邏輯是否正確。例如 Claude 寫出 `def login(): return True` 這種空殼邏輯，安全模型仍可能允許，因為安全 ≠ 正確。

## Auto + Stop Hook = 完整防護

推薦組合：Auto Mode 防止危險操作，Stop Hook 驗證程式真的可運作（例如自動執行 `pytest`、`npm test`、`npm run build`）。

## Don't Ask Mode

用途：沒有人在旁邊批准時使用，例如 CI pipeline、夜間 batch job、自動化任務。流程：Claude 執行 → 工具是否在允許清單？→ Yes 執行 / No 直接拒絕，不會等待人工確認。

## Bypass Permissions

等同 `--dangerously-skip-permissions`，完全跳過檢查。只能使用於 Docker container、VM、Sandbox 環境，不要在個人電腦或公司 production 環境使用。

## 實際使用建議

- **開發新功能**：Plan → Accept Edits → Auto（先分析架構，確認方向，再開 Auto 自動修改）
- **日常 Coding**：Accept Edits（快、可控、修改後自己 review）
- **長時間 Agent 工作**：Auto + Stop Hook
- **CI / 自動化**：Don't Ask

## 最重要的三個觀念

1. **Auto ≠ 完全放任**：Auto 有安全模型檢查
2. **安全與正確是兩件事**：Permission Mode = 防止危險；Test / Hook = 確保品質，兩者需要搭配
3. **權限越高，環境隔離越重要**：信任等級 Manual → Accept Edits → Auto → Don't Ask → Bypass，越往下自動化越高、風險越高

## 建議 Claude Code 工作流

以 AI Engineer / Full Stack 開發情境：需求分析（Plan Mode）→ 架構確認（Accept Edits）→ 大量實作（Auto Mode）→ 完成後（Stop Hook + Tests）→ CI/CD（Don't Ask）。這套方式比較接近目前 AI Agent 開發的最佳實務。
