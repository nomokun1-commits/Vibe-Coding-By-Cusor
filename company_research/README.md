# 企業情報リサーチCLI

企業名を入力するだけで、最新の事業動向・投資・開発などをまとめた調査レポート（Markdown）を自動生成するコマンドラインツール。

## 仕組み（すべて無料の公開API + Claude APIで要約のみ）

情報源:
- **Wikipedia REST API** — 企業概要（無料、APIキー不要）
- **Google News RSS** — 直近の関連ニュース見出し（無料、APIキー不要）
- **EDINET API**（金融庁）— 有価証券報告書などの開示書類（無料、APIキー不要）

要約・整形:
- **Claude API (Haiku 4.5)** — 上記の素材を9セクションのテンプレートに沿って構造化

有料の検索APIや情報取得サービスは使いません。AnthropicのAPI料金のみ発生します（1回あたり概ね数円〜十数円）。

## セットアップ

```bash
pip install -r requirements.txt
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

Anthropic APIキーは https://console.anthropic.com/ で取得できます。

## 使い方

```bash
# 基本: 日本企業
python company_research.py "トヨタ自動車"

# 海外企業（英語のWikipedia/Newsを使い、EDINETはスキップ）
python company_research.py "Apple" --lang en

# 出力先を指定
python company_research.py "任天堂" -o reports/nintendo_latest.md

# ニュース取得件数を増やす
python company_research.py "ソニーグループ" --news-count 40
```

レポートはデフォルトで `reports/<企業名>_<日付>.md` に保存されます。

## レポートの構成

1. 企業概要
2. 最新の事業動向
3. 事業計画・戦略
4. 投資・M&A情報
5. 研究開発・新製品・新サービス
6. 業績・財務情報
7. 業界動向・競合状況
8. 主要ニュース（直近6ヶ月）
9. 情報源（参照URL一覧）

## ファイル構成

```
company_research/
├── company_research.py   # CLIエントリーポイント
├── research.py           # Claude API で要約
├── wikipedia.py          # Wikipedia REST API クライアント
├── news.py               # Google News RSS クライアント
├── edinet.py             # EDINET API クライアント
├── requirements.txt
├── .env.example
└── reports/              # 生成されたレポート（gitignore推奨）
```

## 注意事項

- レポートはClaudeが**提供された素材のみ**を根拠に書くよう指示しています。Web検索はしません。そのため、ニュース見出しに無い詳細（決算数値、人事情報など）は「公開情報からは確認できず」となる場合があります。
- 重要な意思決定の前には、必ず情報源セクションのURLを当たって一次情報を確認してください。
- AIが要約する都合上、誤りが含まれる可能性があります。
