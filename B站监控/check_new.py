"""
B站整合包监控 - 供 GitHub Actions 调用
输出格式：JSON，含新视频列表
"""
import json, os, re, urllib.request, urllib.parse
from datetime import datetime

FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
KWS = ["整合包更新", "整合包发布"]
TAG_KW = "我的世界"
now = datetime.now()
MONTH_START = int(datetime(now.year, now.month, 1).timestamp())


def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read().decode("utf-8", errors="replace")
    except:
        return None


def decode(s):
    try:
        return json.loads('"' + s + '"')
    except:
        return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s)


saved = {}
if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        for v in json.load(f):
            saved[v["bvid"]] = v

all_found = dict(saved)

for kw in KWS:
    for page in range(1, 13):
        url = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(kw)}&order=pubdate&page={page}"
        html = fetch(url)
        if not html:
            break
        for m in re.finditer(r'bvid:"(BV\w{10})"', html):
            bvid = m.group(1)
            if bvid in all_found:
                continue
            chk = html[m.start():m.start() + 1600]
            tm = re.search(r'title:"((?:[^"\\]|\\.)*)"', chk)
            title = decode(tm.group(1)) if tm else ""
            title = re.sub(r'</?em[^>]*>', '', title)
            tgm = re.search(r'tag:"((?:[^"\\]|\\.)*)"', chk)
            tag = decode(tgm.group(1)) if tgm else ""
            pm = re.search(r'pubdate:(\d+)', chk)
            pub = int(pm.group(1)) if pm else 0
            if not any(k in title for k in KWS) or TAG_KW not in tag or pub < MONTH_START:
                continue
            all_found[bvid] = {"bvid": bvid, "title": title, "kw": k, "pub": pub,
                               "url": f"https://www.bilibili.com/video/{bvid}"}

all_list = sorted(all_found.values(), key=lambda x: x["pub"], reverse=True)
month = [v for v in all_list if v["pub"] >= MONTH_START]
new = [v for v in month if v["bvid"] not in saved]

with open(FILE, "w", encoding="utf-8") as f:
    json.dump(month, f, ensure_ascii=False, indent=2)

# 输出 JSON + 结果
result = {"total": len(month), "new": len(new), "videos": new}
print(json.dumps(result, ensure_ascii=False))
