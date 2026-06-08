# ASCT — Agentic Supply Chain Twin

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-dashboard-red?logo=streamlit)
![SQLite](https://img.shields.io/badge/database-SQLite-lightblue?logo=sqlite)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

> 調達・在庫・物流の意思決定を、4体のAIエージェントが自律的に処理するサプライチェーン管理プロトタイプ

需要急増・天候・供給途絶などの外部イベントを検知し、複数の専門エージェントがシナリオを提案、CEOオーケストレーターが信頼スコアをもとに最終決定を下す。すべての判断経緯はDBに記録され、信頼スコアが閾値を下回るケースは自動でエスカレーションされる。

---

## エージェント構成

```
外部イベント（需要急増・天候・供給途絶）
    │
    ▼
CEO Orchestrator（信頼スコアで最終決定）
    ├── DemandForecastAgent  — 需要予測・季節性補正
    ├── SupplyRiskAgent      — 供給リスク評価
    ├── InventoryOptAgent    — 在庫最適化シナリオ生成
    └── LogisticsAgent       — 物流ルート提案
    │
    ▼
Decision Log（SQLite）— 因果チェーン全記録
    ├── 信頼スコア < 閾値 → 人間へエスカレーション
    └── 閾値以上 → 自動実行
```

---

## 主な機能

- 4専門エージェントが連携して意思決定シナリオを提案
- イベントから最終決定までの因果チェーンをすべてDBに記録
- 信頼スコアが閾値を下回ると自動でエスカレーション
- 日本語テキストをLLMなしでシステム設定に変換するルールエンジン
- Streamlitダッシュボードでリアルタイム監視

---

## 技術スタック

| カテゴリ | 技術 |
|---|---|
| バックエンド | FastAPI, SQLAlchemy, Alembic |
| データベース | SQLite |
| UI | Streamlit |
| AI | LLMなし — 決定論的ルールエンジン |

---

## 設計の工夫

- `BaseAgent` を継承して所定ディレクトリに配置するだけで新エージェントを追加できるプラグイン設計
- エージェント間データに「次元・変化量・対象・信頼度」を付与した型付きシグナル形式で判断根拠を追跡可能
- クラウドサービス不使用。SQLite + FastAPI + Streamlit + YAML のみで動作

---

## セットアップ

```bash
pip install -e ".[dev]"
alembic upgrade head
python -m src.seed.generate
uvicorn src.main:app --reload       # API: http://127.0.0.1:8000/docs
streamlit run src/dashboard.py      # UI:  http://127.0.0.1:8501
```

---

## ライセンス

MIT
