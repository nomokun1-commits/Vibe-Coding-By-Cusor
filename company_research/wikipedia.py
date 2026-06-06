"""Wikipedia REST API から企業概要を取得する（無料・APIキー不要）。"""
from __future__ import annotations

import urllib.parse

import requests


def fetch_summary(company: str, lang: str = "ja") -> dict | None:
    """Wikipedia の要約セクションを取得する。見つからなければ None。"""
    title = urllib.parse.quote(company)
    url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "company-research-cli/1.0"})
        if r.status_code != 200:
            return None
        data = r.json()
    except (requests.RequestException, ValueError):
        return None

    return {
        "title": data.get("title", company),
        "extract": data.get("extract", ""),
        "url": (data.get("content_urls", {}).get("desktop", {}).get("page", "")),
    }


def format_wikipedia_summary(summary: dict | None) -> str:
    if not summary or not summary.get("extract"):
        return "（Wikipediaに該当ページは見つかりませんでした）"
    return (
        f"{summary['extract']}\n"
        f"出典: {summary.get('url', '')}"
    )
