# 企業情報リサーチCLI

企業名を入力するだけで、最新の事業計画・投資・開発・動向などをまとめた調査レポート（Markdown）を自動生成するコマンドラインツール。

## 仕組み

- **Claude API（Opus 4.8）** の web_search / web_fetch サーバーサイドツールで最新Web情報を収集
- **EDINET API**（金融庁）で有価証券報告書などの一次情報を補完
- 定型テンプレート（9セクション）で報告書として読みやすい構造に整形

## セットアップ

```bash
# 依存関係をインストール
pip install -r requirements.txt

# APIキーを設定
cp .env.example .env
# .env を編集して ANTHROPIC_API_KEY を設定
```

Anthropic APIキーは https://console.anthropic.com/ で取得できます。

## 使い方

```bash
# 基本: 企業名を1つ渡すだけ
python company_research.py "トヨタ自動車"

# EDINET検索をスキップ（海外企業など）
python company_research.py "Apple Inc." --no-edinet

# 出力先を指定
python company_research.py "任天堂" -o reports/nintendo_latest.md

# EDINETを遡る期間を指定（デフォルト90日）
python company_research.py "ソニーグループ" --edinet-days 180
```

レポートは `reports/<企業名>_<日付>.md` に保存されます（デフォルト）。

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
├── research.py           # Claude APIによるリサーチ本体
├── edinet.py             # EDINET API クライアント
├── requirements.txt
├── .env.example
└── reports/              # 生成されたレポート（gitignore推奨）
```

## コストの目安

1回あたり概ね $0.30〜$1.00 程度（リサーチの深さと使うWeb検索回数による）。
コストを抑えたい場合は `research.py` の `MODEL` を `claude-sonnet-4-6` に変更してください。

## 注意

- 生成された情報は必ず人間がファクトチェックしてください。AIは間違える可能性があります。
- 情報源セクションのURLを必ず確認し、重要な意思決定の根拠とする前に一次情報を当たってください。
