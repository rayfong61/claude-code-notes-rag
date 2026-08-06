---
name: verification
description: Run after completing any change to backend/, tests/, or scripts/. Verifies tests pass, diff matches the request, and no test assertions were weakened.
---

# Verification Skill

跑 `.claude/skills/verification/verify.sh`（等同 `pytest -q`），並回報結果。

完成任何後端改動後，依序執行：

1. 執行 `verify.sh`，確認測試全數通過。
2. 查看 `git diff`，確認修改的檔案與需求相符，沒有動到不相關模組。
3. 確認測試斷言沒有被弱化（例如把 `assert x == y` 改成 `assert x is not None` 這類降低驗證強度的改動）。
4. 回報：跑了什麼、測試結果、diff 摘要——不要只說「完成了」。

Done 的定義是「驗證流程執行 + 結果被確認」，不是「Claude 說完成」。
