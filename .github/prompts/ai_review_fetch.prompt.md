---
mode: agent
---
Step1.請依照輸入的 MR_ID，執行以下指令 :
`python ai_review/gitlab_mr.py <MR_ID> --fetch --diff`

Step2.等執行完後，再詢問使用者要執行哪一項?
1. 簡易審查模式，並執行`/start_review_low.prompt.md`。
2. 深度審查模式，並執行`/start_review_high.prompt.md`。