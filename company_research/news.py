"""Google News RSS から企業関連ニュースを取得する（無料・APIキー不要）。"""
from __future__ import annotations

import urllib.parse
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

import requests


class _TagStripper(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _strip_html(text: str) -> str:
    parser = _TagStripper()
    parser.feed(text)
    return " ".join("".join(parser.parts).split())


def fetch_news(company: str, limit: int = 20, lang: str = "ja") -> list[dict]:
    """Google News RSS で企業名を検索し、最新ニュースのリストを返す。"""
    q = urllib.parse.quote(company)
    if lang == "ja":
        url = f"https://news.google.com/rss/search?q={q}&hl=ja&gl=JP&ceid=JP:ja"
    else:
        url = f"https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
    except requests.RequestException:
        return []

    items: list[dict] = []
    try:
        root = ET.fromstring(r.content)
    except ET.ParseError:
        return []

    for item in root.iterfind(".//item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source = item.findtext("source") or ""
        desc_raw = item.findtext("description") or ""
        description = _strip_html(desc_raw)
        items.append(
            {
                "title": title,
                "link": link,
                "pub_date": pub_date,
                "source": source.strip(),
                "description": description,
            }
        )
        if len(items) >= limit:
            break
    return items


def format_news_summary(items: list[dict], limit: int = 15) -> str:
    if not items:
        return "（Google Newsで関連ニュースは見つかりませんでした）"
    lines = []
    for it in items[:limit]:
        date = it["pub_date"][:16] if it["pub_date"] else "日付不明"
        src = f"[{it['source']}] " if it["source"] else ""
        lines.append(f"- {date} {src}{it['title']}\n  {it['link']}")
    return "\n".join(lines)
