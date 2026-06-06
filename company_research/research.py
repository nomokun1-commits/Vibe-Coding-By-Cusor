"""Claude APIを使った企業情報リサーチ。

Anthropic公式SDKの web_search / web_fetch サーバーサイドツールで
最新情報を収集し、定型テンプレートで報告書を生成する。
"""
from __future__ import annotations

import datetime as dt

import anthropic

MODEL = "claude-opus-4-8"

REPORT_TEMPLATE = """\
# {company} 企業調査レポート

調査日: {date}

## 1. 企業概要
（事業内容、本社所在地、設立年、代表者、従業員数、上場区分など）

## 2. 最新の事業動向
（直近の主要な動き、戦略的な変化、組織再編など)

## 3. 事業計画・戦略
（中期経営計画、今後の事業方針、注力分野など）

## 4. 投資・M&A情報
（最近の投資案件、買収・売却、出資、提携など）

## 5. 研究開発・新製品・新サービス
（R&D投資、新製品発表、技術開発、特許など）

## 6. 業績・財務情報
（直近の決算サマリー、売上・利益、財務状態など）

## 7. 業界動向・競合状況
（業界全体のトレンド、主要競合、市場ポジションなど）

## 8. 主要ニュース（直近6ヶ月）
（重要なニュース・発表を時系列で）

## 9. 情報源
（参照したURL一覧）
"""


SYSTEM_PROMPT = """\
あなたは企業調査専門のリサーチアナリストです。
日本語で、ビジネス報告書として通用する明確で簡潔な文章を書きます。

調査の進め方:
1. web_search ツールで最新情報を複数の信頼できるソース (公式IR、日経、東洋経済、Bloomberg、Reuters など) から収集する
2. 必要に応じて web_fetch ツールで重要なページの詳細を取得する
3. 推測や憶測は書かず、確認できた事実のみを記載する
4. 情報源が不明な項目は「公開情報からは確認できず」と明記する
5. 提示されたテンプレートの全セクションを埋める
6. 各事実の根拠となるURLを情報源セクションにまとめる

日付の基準: 本日は {today}。「最新」とは過去6ヶ月以内の情報を指す。
"""


def research_company(company_name: str, edinet_summary: str | None = None) -> str:
    """企業名を受け取り、Markdown形式の調査レポートを返す。"""
    client = anthropic.Anthropic()
    today = dt.date.today().isoformat()

    user_prompt = (
        f"以下のテンプレートに従って「{company_name}」の企業調査レポートを作成してください。\n\n"
        f"テンプレート:\n{REPORT_TEMPLATE.format(company=company_name, date=today)}\n"
    )
    if edinet_summary:
        user_prompt += (
            f"\n参考: EDINET (金融庁開示書類API) で取得した直近の開示書類:\n"
            f"{edinet_summary}\n"
            "これらの一次情報も活用してください。\n"
        )

    response = client.messages.create(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT.format(today=today),
        thinking={"type": "adaptive"},
        tools=[
            {"type": "web_search_20260209", "name": "web_search"},
            {"type": "web_fetch_20260209", "name": "web_fetch"},
        ],
        messages=[{"role": "user", "content": user_prompt}],
    )

    parts: list[str] = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()
