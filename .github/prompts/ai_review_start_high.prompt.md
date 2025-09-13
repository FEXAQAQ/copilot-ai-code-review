---
mode: agent
---
請根據 `ai_review/review_rule.md` 中的審查標準，針對 `ai_review/mr_diff.md` 所列的程式碼差異進行審查，並依據 `ai_review/mr_request.md` 裡的描述協助理解改動背景。

若 `ai_review/mr_diff.md` 中出現檔案名稱與變更位置（如路徑與行號），請主動查閱該檔案的上下文（例如 interface 定義、相依 function、使用場景等），不要只根據 diff 做片面的判斷。

本次改動可能牽涉跨檔案邏輯與 interface 相容性，請從程式碼整體設計面進行全面性檢查，尤其注意以下幾點：
- 是否違反任何 `ai_review/review_rule.md` 的規則
- 是否有未更新的相依程式碼（如呼叫端、實作端）
- 是否會破壞既有邏輯或使用情境

請將完整的審查結果以 Markdown 格式寫入 `ai_review/output_review.md`。