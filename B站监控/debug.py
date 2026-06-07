import subprocess, re

url = "https://search.bilibili.com/all?keyword=%E6%95%B4%E5%90%88%E5%8C%85%E6%9B%B4%E6%96%B0&order=pubdate"

r = subprocess.run(
    ["curl.exe", "-s", "-L",
     "-A", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
     "-H", "Accept-Language: zh-CN,zh;q=0.9",
     "--connect-timeout", "15", "--max-time", "30", url],
    capture_output=True, timeout=35
)

text = r.stdout.decode("utf-8", errors="replace")

# 找一个完整视频条目
m = re.search(r'bvid:"(BV[a-zA-Z0-9]{10})"', text)
if m:
    start = m.start()
    chunk = text[max(0,start-100):start+800]
    print("=== 第一个视频条目原始数据 ===")
    print(chunk)
    print()

# 找 tag 字段
tags_found = re.findall(r'tag:"([^"]*)"', text)
print(f"tag字段出现次数: {len(tags_found)}")
for t in tags_found[:10]:
    if t:
        print(f"  tag: [{t}]")

# 解析并显示前10个视频
pattern = r'bvid:"(BV[a-zA-Z0-9]{10})"'
count = 0
for m in re.finditer(pattern, text):
    bvid = m.group(1)
    pos = m.start()
    chunk = text[max(0,pos-100):pos+600]

    tm = re.search(r'title:"([^"]*)"', chunk)
    title = tm.group(1) if tm else ""
    title = re.sub(r'<em class="keyword">', '', title)
    title = re.sub(r'</em>', '', title)
    # decode unicode escapes
    title = title.encode().decode("unicode_escape", errors="replace")

    tm = re.search(r'tag:"([^"]*)"', chunk)
    tag = tm.group(1) if tm else "(无tag)"

    count += 1
    print(f"\n{count}. [{bvid}]")
    print(f"   标题: {title[:80]}")
    print(f"   标签: [{tag}]")

    if count >= 10:
        break
