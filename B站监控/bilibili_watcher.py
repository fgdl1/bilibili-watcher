# -*- coding: utf-8 -*-
"""
B站 整合包视频 — 本月汇总
"""

import subprocess
import re
import json
import os
import sys
import time
import urllib.parse
from datetime import datetime

# 启用 CMD ANSI 颜色
if sys.platform == "win32":
    import ctypes
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)

KW_TYPES = {
    "整合包更新": "\033[32m",  # 绿色
    "整合包发布": "\033[33m",  # 黄色
}
RESET = "\033[0m"
TAG_KW = "我的世界"

BASE = os.path.dirname(os.path.abspath(__file__))
VIDEO_FILE = os.path.join(BASE, "bilibili_videos.json")
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

now = datetime.now()
MONTH_START = int(datetime(now.year, now.month, 1).timestamp())

# 预估总页数（每关键词10页足够覆盖当月）
MAX_PAGES = 15
TOTAL_PAGES = len(KW_TYPES) * MAX_PAGES


def d(s):
    try:
        return json.loads('"' + s + '"')
    except:
        return re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), s).replace('\\"', '"').replace('\\/', '/')


def fetch(url):
    try:
        r = subprocess.run(
            ["curl.exe", "-s", "-L", "-A", UA,
             "--connect-timeout", "6", "--max-time", "10", url],
            capture_output=True, timeout=15
        )
        if r.returncode == 0 and r.stdout:
            return r.stdout.decode("utf-8", errors="replace")
    except:
        pass
    return None


def main():
    print(f"\033[36m{'='*60}\033[0m")
    print(f"  B站 整合包视频 — {now.month}月")
    print(f"\033[36m{'='*60}\033[0m")

    saved = {}
    if os.path.exists(VIDEO_FILE):
        with open(VIDEO_FILE, "r", encoding="utf-8") as f:
            for v in json.load(f):
                saved[v["bvid"]] = v

    all_found = dict(saved)
    page_done = 0

    for kw in KW_TYPES:
        for page in range(1, MAX_PAGES + 1):
            url = f"https://search.bilibili.com/all?keyword={urllib.parse.quote(kw)}&order=pubdate&page={page}"
            html = fetch(url)
            if not html:
                page_done += (MAX_PAGES - page + 1)
                break

            for m in re.finditer(r'bvid:"(BV\w{10})"', html):
                bvid = m.group(1)
                if bvid in all_found:
                    continue
                chunk = html[m.start():m.start() + 1600]

                tm = re.search(r'title:"((?:[^"\\]|\\.)*)"', chunk)
                title = d(tm.group(1)) if tm else ""
                title = re.sub(r'</?em[^>]*>', '', title)

                tgm = re.search(r'tag:"((?:[^"\\]|\\.)*)"', chunk)
                tag = d(tgm.group(1)) if tgm else ""

                am = re.search(r'author:"([^"]*)"', chunk)
                author = am.group(1) if am else ""

                pm = re.search(r'pubdate:(\d+)', chunk)
                pubdate = int(pm.group(1)) if pm else 0

                fm = re.search(r'play:(\d+)', chunk)
                play = int(fm.group(1)) if fm else 0

                # 匹配关键词类型
                vkw = ""
                for k in KW_TYPES:
                    if k in title:
                        vkw = k
                        break
                if not vkw or TAG_KW not in tag or pubdate < MONTH_START:
                    continue

                all_found[bvid] = {
                    "bvid": bvid, "title": title, "author": author,
                    "kw": vkw, "pubdate": pubdate,
                    "pubtime": datetime.fromtimestamp(pubdate).strftime("%m-%d %H:%M"),
                    "url": f"https://www.bilibili.com/video/{bvid}",
                    "play": play,
                }

            page_done += 1
            pct = page_done * 100 // TOTAL_PAGES
            bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
            print(f"\r  [{bar}] {pct}%", end="", flush=True)

            # 已经翻到本月之前的数据，停止该关键词
            if page >= 2:
                pts = [int(p) for p in re.findall(r'pubdate:(\d+)', html) if p]
                if pts and max(pts) < MONTH_START:
                    page_done += (MAX_PAGES - page)
                    break

    print(f"\r  [{'█'*20}] 100%")

    videos = sorted(all_found.values(), key=lambda v: v["pubdate"], reverse=True)
    month = [v for v in videos if v["pubdate"] >= MONTH_START]
    new = [v for v in month if v["bvid"] not in saved]

    with open(VIDEO_FILE, "w", encoding="utf-8") as f:
        json.dump(month, f, ensure_ascii=False, indent=2)

    print(f"\n  本月 {len(month)} 个" + (f"  (新 {len(new)} 个)" if new else ""))
    print(f"  {'─'*50}")

    if not month:
        print("  暂无")
    else:
        for i, v in enumerate(month, 1):
            c = KW_TYPES.get(v.get("kw", ""), "")
            tag = " [新]" if v["bvid"] in {n["bvid"] for n in new} else ""
            print(f"  {i:2d}.{c} {v['title']}{tag}{RESET}  ▶{v['play']}  {v['pubtime']}")
            print(f"       {v['url']}")

    input(f"\n 按回车退出...")


if __name__ == "__main__":
    main()
