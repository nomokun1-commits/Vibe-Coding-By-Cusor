"""Claude API で収集済み素材を要約し、定型レポートを生成する。

Web検索などの有料API呼び出しは行わない。
情報は事前に収集された素材 (Wikipedia / Google News RSS / EDINET) を
Claudeに渡して構造化・要約してもらう。
"""
from __future__ import annotations

import datetime as dt

import anthropic

MODEL = "claude-haiku-4-5"  # 安価なモデルで要約

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

執筆ルール:
1. 提供された素材 (Wikipedia / Google Newsの見出し / EDINETの開示一覧) のみを根拠とする
2. 推測や憶測、素材にない情報は書かない
3. 確認できない項目は「公開情報からは確認できず」と明記する
4. 提示されたテンプレートの全セクションを必ず埋める（情報がなくても見出しは残す）
5. 各事実の根拠となるURLを情報源セクションにまとめる
6. ニュース見出しから読み取れる動向は要約してよいが、見出しに無い詳細を捏造しない

日付の基準: 本日は {today}。「最新」とは過去6ヶ月以内の情報を指す。
"""


def build_user_prompt(
    company: str,
    wikipedia_summary: str,
    news_summary: str,
    edinet_summary: str,
) -> str:
    today = dt.date.today().isoformat()
    return (
        f"以下のテンプレートに沿って「{company}」の企業調査レポートを作成してください。\n"
        f"素材として渡す情報源だけを根拠にしてください。\n\n"
        f"=== テンプレート ===\n"
        f"{REPORT_TEMPLATE.format(company=company, date=today)}\n"
        f"=== Wikipedia 要約 ===\n{wikipedia_summary}\n\n"
        f"=== Google News (直近の関連ニュース見出し) ===\n{news_summary}\n\n"
        f"=== EDINET (直近の開示書類) ===\n{edinet_summary}\n"
    )


def synthesize_report(
    company: str,
    wikipedia_summary: str,
    news_summary: str,
    edinet_summary: str,
) -> str:
    client = anthropic.Anthropic()
    today = dt.date.today().isoformat()

    response = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT.format(today=today),
        messages=[
            {
                "role": "user",
                "content": build_user_prompt(
                    company, wikipedia_summary, news_summary, edinet_summary
                ),
            }
        ],
    )

    parts: list[str] = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts).strip()
