#!/usr/bin/env python3
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

FEED_URL = "https://www.abhik.ai/rss/feed.xml"
README = "Readme.md"
MAX = 5

feed = urllib.request.urlopen(FEED_URL).read()
root = ET.fromstring(feed)

NS = "http://www.w3.org/2005/Atom"
entries = root.findall(f"{{{NS}}}entry")

if entries:
    def get_title(e): return e.findtext(f"{{{NS}}}title", "").strip()
    def get_url(e):
        link = e.find(f"{{{NS}}}link")
        return link.get("href", "") if link is not None else ""
    def get_date(e): return e.findtext(f"{{{NS}}}published", "")[:10]
else:
    entries = root.findall(".//item")
    def get_title(e): return (e.findtext("title") or "").strip()
    def get_url(e): return (e.findtext("link") or "").strip()
    def get_date(e):
        from email.utils import parsedate
        d = e.findtext("pubDate") or ""
        p = parsedate(d)
        return f"{p[0]}-{p[1]:02d}-{p[2]:02d}" if p else d[:10]

lines = []
for e in entries[:MAX]:
    title, url, date = get_title(e), get_url(e), get_date(e)
    try:
        date = datetime.fromisoformat(date).strftime("%b %d, %Y")
    except ValueError:
        pass
    lines.append(f"- [{title}]({url}) <sub>{date}</sub>")

block = "<!-- BLOG-POST-LIST:START -->\n" + "\n".join(lines) + "\n<!-- BLOG-POST-LIST:END -->"

with open(README) as f:
    content = f.read()

content = re.sub(
    r"<!-- BLOG-POST-LIST:START -->.*?<!-- BLOG-POST-LIST:END -->",
    block, content, flags=re.DOTALL,
)

with open(README, "w") as f:
    f.write(content)

print(f"Updated {len(lines)} posts")
