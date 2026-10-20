import sys
import requests
from pathlib import Path
import re, json
from urllib.parse import urlparse
from datetime import datetime

OUTPUT_DIR = Path("public/archive")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; ArchiveBot/1.0)",
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8"
}

def safe_filename(url: str) -> str:
    p = urlparse(url)
    name = p.netloc + p.path + ("_" + p.query if p.query else "")
    name = re.sub(r'[^a-zA-Z0-9._-]', '_', name).strip('_')
    if len(name) > 120:
        name = name[:120]
    return f"{name}.html" if name else "index.html"

def main():
    if len(sys.argv) < 2:
        print("URLが渡されていません")
        return
    url = sys.argv[1].strip()
    print(f"Downloading: {url}")

    # robots.txtはリクエストしない = 無視する実装
    res = requests.get(url, headers=HEADERS, timeout=30)
    res.raise_for_status()

    filename = safe_filename(url)
    (OUTPUT_DIR / filename).write_bytes(res.content)
    print(f"Saved to {OUTPUT_DIR / filename}")

    # 一覧JSONを更新
    list_path = OUTPUT_DIR / "list.json"
    data = []
    if list_path.exists():
        try:
            data = json.loads(list_path.read_text(encoding="utf-8"))
        except:
            data = []
    
    data.insert(0, {
        "url": url,
        "file": filename,
        "saved_at": datetime.now().isoformat()
    })
    # 重複URLは最新だけ残す
    seen = set()
    uniq = []
    for item in data:
        if item["url"] not in seen:
            uniq.append(item)
            seen.add(item["url"])
    list_path.write_text(json.dumps(uniq, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
