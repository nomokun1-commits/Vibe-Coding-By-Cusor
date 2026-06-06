"""EDINET API クライアント

金融庁が提供する有価証券報告書等の開示書類API。
APIキーなしでも基本的な検索は可能。
ドキュメント: https://disclosure2dl.edinet-fsa.go.jp/guide/static/disclosure/WZEK0110.html
"""
from __future__ import annotations

import datetime as dt
import os
from typing import Optional

import requests

EDINET_BASE = "https://api.edinet-fsa.go.jp/api/v2"


def _api_key_params() -> dict:
    key = os.environ.get("EDINET_API_KEY")
    return {"Subscription-Key": key} if key else {}


def search_recent_documents(company_keyword: str, days: int = 90) -> list[dict]:
    """直近N日間の開示書類を検索し、企業名にマッチするものを返す。

    EDINET APIは日付ごとに書類リストを取得する形式のため、
    一定期間を走査して企業名をフィルタする。
    """
    matched: list[dict] = []
    today = dt.date.today()
    for i in range(days):
        date = today - dt.timedelta(days=i)
        url = f"{EDINET_BASE}/documents.json"
        params = {"date": date.isoformat(), "type": 2, **_api_key_params()}
        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError):
            continue
        for doc in data.get("results", []):
            name = doc.get("filerName") or ""
            if company_keyword in name:
                matched.append(
                    {
                        "date": date.isoformat(),
                        "filer": name,
                        "doc_description": doc.get("docDescription"),
                        "doc_id": doc.get("docID"),
                        "edinet_code": doc.get("edinetCode"),
                    }
                )
    return matched


def format_edinet_summary(docs: list[dict], limit: int = 10) -> str:
    if not docs:
        return "（EDINETで該当する開示書類は見つかりませんでした）"
    lines = []
    for d in docs[:limit]:
        lines.append(
            f"- {d['date']} | {d['filer']} | {d['doc_description']} (docID: {d['doc_id']})"
        )
    return "\n".join(lines)
