"""企業情報リサーチCLI

使い方:
    python company_research.py "トヨタ自動車"
    python company_research.py "ソニーグループ" --no-edinet
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
from research import research_company


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^\w\-_.]", "_", name)
    return cleaned[:80]


def main() -> int:
    parser = argparse.ArgumentParser(description="企業情報を調査してMarkdownレポートを生成します。")
    parser.add_argument("company", help="調査対象の企業名（例: トヨタ自動車）")
    parser.add_argument(
        "--no-edinet",
        action="store_true",
        help="EDINET (金融庁) の検索をスキップする（高速化用）",
    )
    parser.add_argument(
        "--edinet-days",
        type=int,
        default=90,
        help="EDINETを遡る日数（デフォルト: 90日）",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="出力ファイルパス（省略時は reports/<企業名>_<日付>.md）",
    )
    args = parser.parse_args()

    load_dotenv()
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("エラー: ANTHROPIC_API_KEY が設定されていません。.env を作成してください。", file=sys.stderr)
        return 1

    edinet_summary: str | None = None
    if not args.no_edinet:
        print(f"[1/2] EDINETで {args.company} の開示書類を検索中（過去{args.edinet_days}日）...", file=sys.stderr)
        docs = search_recent_documents(args.company, days=args.edinet_days)
        edinet_summary = format_edinet_summary(docs)
        print(f"      → {len(docs)} 件ヒット", file=sys.stderr)

    print(f"[2/2] Claudeで Web 検索とレポート生成中（数分かかります）...", file=sys.stderr)
    report = research_company(args.company, edinet_summary=edinet_summary)

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
