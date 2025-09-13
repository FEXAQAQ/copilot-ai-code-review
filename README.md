# GitLab MR Copilot AI Review 系統

此工具能協助你使用 GitLab API、VS Code Copilot 以及 markdown 審查規則，自動化 Merge Request (MR) 的審查與留言流程。

## 📂 專案結構

```
ai_review/
├── config.json           ← 設定檔：Gitlab相關資訊
├── gitlab_mr.py          ← 主程式：操作GitLab MR 的抓取/留言/Approve
├── mr_request.md         ← 自動生成：儲存 MR 的 ID、標題與說明
├── mr_diff.md            ← 自動生成：儲存 MR 的程式碼變更差異（diff）
├── review_rule.md        ← 審查規則：提供 Copilot 使用的規則文件
└── output_review.md      ← Copilot 產生的審查建議

.github/
└── prompts/              ← Copilot Chat 指令模板
    ├── fetch.prompt.md             ← 抓取 MR 資料的指令模板
    ├── start_review_low.prompt.md  ← 簡易審查模式指令模板
    ├── start_review_high.prompt.md ← 深度審查模式指令模板
    └── comment.prompt.md           ← 留言至 MR 的指令模板
```

## ⚙️ 如何安裝

### 步驟 1：這兩個資料夾複製到你的專案根目錄即可

### 步驟 2：到ai_review/config.json設定
- 編輯 `config.json`，填入您的 GitLab 資訊：
```json
   {
     "gitlab": {
       "domain": "gitlab.公司網域.com",
       "token": "你申請的Gitlab Token",
       "project_id": "Gitalb上的專案路徑"
     }
   }
```
- Token 取得方式
1. 前往 GitLab > Settings > Access Tokens
2. 建議權限至少包含：
   - `api`
   - `read_repository`
   - `write_repository`（若需要 approve）

### 步驟 3：安裝 Python

## 🚀 運作流程說明

### 步驟 1：Checkout Merge Request Branch

**說明：** 先切換到MR分支。

### 步驟 2：抓取MR上的資料 & 程式碼差異

**說明：** 在 VS Code 的 Copilot Chat 中(Agent模式下)，使用以下指令：

```
/ai_review_fetch <MR_ID>
```

此指令會自動執行以下動作 :
- 抓取該 Merge Request 的 ID、標題、描述，並儲存至 `ai_review/mr_request.md`
- 抓取該 Merge Request 的程式碼變更差異（diff），並儲存至 `ai_review/mr_diff.md`

### 步驟 3：使用 Copilot 進行審查

**說明：** 當執行完步驟2時，Copilot會根據審查需求讓你選擇適當的審查模式：

#### 1.簡易審查模式

**說明：** 執行基礎程式碼審查，根據 `review_rule.md` 的審查標準進行檢視，適合一般的程式碼變更。

#### 2.深度審查模式

**說明：** 執行深度程式碼審查，除了基礎審查外，還會：
- 主動查閱變更檔案的上下文（interface 定義、相依 function、使用場景等）
- 檢查跨檔案邏輯與 interface 相容性
- 從程式碼整體設計面進行全面性檢查
- 檢查是否有未更新的相依程式碼

兩種模式都會將審查結果輸出到 `ai_review/output_review.md`。

### 步驟 4：將審查結果提交到 MR 留言

```
/ai_review_comment <MR_ID>
```

**說明：** 此指令會自動將 `output_review.md` 的內容作為留言貼到該 Merge Request。

### 步驟 5：（可選）Approve 該 MR

```bash
python ai_review/gitlab_mr.py <MR_ID> --approve
```

**說明：** 將此 MR 直接 Approve（需要你有 Approver 權限）。

## 🛠️ 指令總覽

### Copilot Chat 指令
| 指令                        | 功能說明                                    |
|----------------------------|-------------------------------------------|
| `/fetch <MR_ID>`           | 擷取 MR 說明與差異，產生 mr_request.md 和 mr_diff.md |
| `/start_review_low`        | 執行簡易程式碼審查，產生 output_review.md    |
| `/start_review_high`       | 執行深度程式碼審查，產生 output_review.md    |
| `/comment <MR_ID>`         | 將 output_review.md 內容留言至 MR         |

### 終端機指令（直接使用）
| 參數        | 功能說明                         |
|-------------|---------------------------------|
| `--fetch`   | 擷取 MR 說明並產生 mr_request.md |
| `--diff`    | 擷取 MR 差異，產生 mr_diff.md     |
| `--comment` | 將 output_review.md 留言至 MR    |
| `--approve` | Approve 該 MR                   |
