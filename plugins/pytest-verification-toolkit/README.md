# pytest-verification-toolkit

打包自這個專案的 `.claude/settings.json`（Hooks 部分）與 `.claude/skills/verification/`，示範「Package Once It Works」——把已經穩定運作的驗證流程打包成可安裝的 Plugin，供其他 pytest 專案重用。

## 內含元件

- **Hook**（`hooks/hooks.json`）：`PostToolUse` 監聽 Edit/Write，自動跑 `pytest -q`，失敗則阻擋（`exit 2`）。
- **Skill**（`skills/verification/`）：引導 Claude 在改完程式碼後依序跑測試、看 diff、確認斷言沒被弱化，才算真正完成。

## 本機測試安裝

`plugins/` 目錄本身是一個本機 Marketplace（見 `plugins/.claude-plugin/marketplace.json`），在 Claude Code 互動模式下執行：

```
/plugin marketplace add C:\Learn\learn_claude_code\plugins
/plugin install pytest-verification-toolkit@learn-claude-code-marketplace
/reload-plugins
```

`/plugin` 系列是互動指令，需要在真正的 Claude Code session 裡手動執行確認（無法由 Claude 自動代跑），實際指令參數請以當時終端機顯示為準。

安裝前建議依 Plugins 筆記的原則，先讀過 `hooks/hooks.json` 內容再裝——這個 Hook 會在每次 Edit/Write 後自動執行 `pytest -q`。
