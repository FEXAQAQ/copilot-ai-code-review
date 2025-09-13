import requests
import os
import argparse
import json

# === 📄 讀取配置檔案 ===
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    
    if not os.path.exists(config_path):
        print(f"❌ 找不到配置檔案：{config_path}")
        print("請建立 config.json 檔案並設定相關參數")
        exit(1)
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ 配置檔案格式錯誤：{e}")
        exit(1)
    except Exception as e:
        print(f"❌ 讀取配置檔案失敗：{e}")
        exit(1)

# === 📁 初始化配置 ===
config = load_config()
GITLAB_TOKEN = config["gitlab"]["token"]
PROJECT_ID = config["gitlab"]["project_id"]
DOMAIN = config["gitlab"]["domain"]

# 檔案路徑設置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MR_FILE = os.path.join(BASE_DIR, config["files"]["mr_request"])
REVIEW_FILE = os.path.join(BASE_DIR, config["files"]["review_output"])
DIFF_FILE = os.path.join(BASE_DIR, config["files"]["mr_diff"])

# 設定參數
REQUEST_TIMEOUT = config["settings"]["request_timeout"]
ENCODING = config["settings"]["encoding"]
AUTO_CLEAR_OUTPUT = config["settings"]["auto_clear_output"]

# === 📥 抓取 MR 資訊並存檔 ===
def fetch_mr_details(mr_iid):
    print(f"取得 MR {mr_iid} 的詳細資訊...")
    url = f"https://{DOMAIN}/api/v4/projects/{PROJECT_ID}/merge_requests/{mr_iid}"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ 無法取得 MR 資料：{e}")
        return False

    mr = response.json()
    content = f"""# MR Request Info

**ID:** {mr['iid']}
**Title:** {mr['title']}

---

{mr['description']}
"""
    
    try:
        with open(MR_FILE, "w", encoding=ENCODING) as f:
            f.write(content)
        print(f"✅ MR 說明已寫入：{MR_FILE}")
        return True
    except Exception as e:
        print(f"❌ 寫入檔案失敗：{e}")
        return False

# === 📄 抓取 MR 差異（Diff）並存檔 ===
def fetch_mr_diff(mr_iid):
    url = f"https://{DOMAIN}/api/v4/projects/{PROJECT_ID}/merge_requests/{mr_iid}/changes"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"❌ 無法取得 MR Diff：{e}")
        return False

    changes = response.json().get("changes", [])
    
    try:
        with open(DIFF_FILE, "w", encoding=ENCODING) as f:
            for c in changes:
                f.write(f"### {c['new_path']}\n")
                f.write("```diff\n")
                f.write(c["diff"])
                f.write("\n```\n\n")
        
        print(f"✅ MR Diff 已寫入：{DIFF_FILE}")
        return True
    except Exception as e:
        print(f"❌ 寫入檔案失敗：{e}")
        return False

# === 💬 將 review 結果留言到 MR ===
def post_mr_comment(mr_iid):
    if not os.path.exists(REVIEW_FILE):
        print(f"❌ 找不到 review 檔案：{REVIEW_FILE}")
        return False

    try:
        with open(REVIEW_FILE, "r", encoding=ENCODING) as f:
            content = f.read().strip()
        
        if not content:
            print("❌ Review 檔案內容為空")
            return False
            
    except Exception as e:
        print(f"❌ 讀取檔案失敗：{e}")
        return False

    url = f"https://{DOMAIN}/api/v4/projects/{PROJECT_ID}/merge_requests/{mr_iid}/notes"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}
    data = {"body": content}
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        
        print("✅ 成功留言至 MR")
        
        # 根據配置決定是否清空檔案
        if AUTO_CLEAR_OUTPUT:
            with open(REVIEW_FILE, "w", encoding=ENCODING) as f:
                f.write("")
            print(f"✅ 已初始化檔案內容：{REVIEW_FILE}")
            
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ 留言失敗：{e}")
        return False

# === ✅ Approve MR ===
def approve_mr(mr_iid):
    url = f"https://{DOMAIN}/api/v4/projects/{PROJECT_ID}/merge_requests/{mr_iid}/approve"
    headers = {"PRIVATE-TOKEN": GITLAB_TOKEN}

    try:
        response = requests.post(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        print("✅ MR 已通過審核（Approved）")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Approve 失敗：{e}")
        return False

# === 🚀 CLI 主程式 ===
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GitLab MR AI Review 工具")
    parser.add_argument("mr_iid", help="Merge Request 的 IID（專案內部 ID）")
    parser.add_argument("--fetch", action="store_true", help="下載 MR 說明至 mr_request.md")
    parser.add_argument("--diff", action="store_true", help="下載 MR 差異內容至 mr_diff.md")
    parser.add_argument("--comment", action="store_true", help="留言 output_review.md 至 MR")
    parser.add_argument("--approve", action="store_true", help="Approve 該 MR")
    args = parser.parse_args()

    if not any([args.fetch, args.comment, args.approve]):
        print("❌ 請至少指定一個操作：--fetch、--comment 或 --approve")
        exit(1)

    if args.fetch:
        fetch_mr_details(args.mr_iid)

    if args.diff:
        fetch_mr_diff(args.mr_iid)

    if args.comment:
        post_mr_comment(args.mr_iid)

    if args.approve:
        approve_mr(args.mr_iid)
    

