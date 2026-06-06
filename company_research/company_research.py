"""企業情報リサーチCLI（無料公開API版）

使い方:
    python company_research.py "トヨタ自動車"
    python company_research.py "Apple" --lang en --no-edinet
    python company_research.py "任天堂" --output reports/nintendo.md
"""
from __future__ import annotations

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv

from edinet import format_edinet_summary, search_recent_documents
from news import fetch_news, format_news_summary
from research import synthesize_report
from wikipedia import fetch_summary, format_wikipedia_summary


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\-_.]", "_", name)
    return cleaned[:80]


def main() -> int:
    parser = argparse.ArgumentParser(description="企業情報を調査してMarkdownレポートを生成します。")
    parser.add_argument("company", help="調査対象の企業名（例: トヨタ自動車）")
    parser.add_argument("--lang", default="ja", choices=["ja", "en"], help="情報源の言語（デフォルト: ja）")
    parser.add_argument("--no-edinet", action="store_true", help="EDINET (金融庁) の検索をスキップ")
    parser.add_argument("--edinet-days", type=int, default=90, help="EDINETを遡る日数（デフォルト: 90）")
    parser.add_argument("--news-count", type=int, default=20, help="取得するニュース見出しの上限（デフォルト: 20）")
    parser.add_argument("--output", "-o", type=Path, default=None, help="出力ファイルパス")
    args = parser.parse_args()

    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY が設定されていません。.env を作成してください。", file=sys.stderr)
        return 1

    print(f"[1/4] Wikipedia ({args.lang}) で概要を取得中...", file=sys.stderr)
    wiki = fetch_summary(args.company, lang=args.lang)
    wiki_summary = format_wikipedia_summary(wiki)

    print(f"[2/4] Google News で関連ニュースを取得中...", file=sys.stderr)
    news_items = fetch_news(args.company, limit=args.news_count, lang=args.lang)
    news_summary = format_news_summary(news_items)
    print(f"      → {len(news_items)} 件取得", file=sys.stderr)

    if args.no_edinet or args.lang != "ja":
        edinet_summary = "（EDINET検索はスキップされました）"
    else:
        print(f"[3/4] EDINETで開示書類を検索中（過去{args.edinet_days}日）...", file=sys.stderr)
        docs = search_recent_documents(args.company, days=args.edinet_days)
        edinet_summary = format_edinet_summary(docs)
        print(f"      → {len(docs)} 件ヒット", file=sys.stderr)

    print(f"[4/4] Claudeでレポート生成中...", file=sys.stderr)
    report = synthesize_report(args.company, wiki_summary, news_summary, edinet_summary)

    if args.output:
        output_path = args.output
    else:
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        today = dt.date.today().isoformat()
        output_path = reports_dir / f"{safe_filename(args.company)}_{today}.md"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"\n完了: {output_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
