# ASCT — Agentic Supply Chain Twin

> マルチエージェント AI がサプライチェーン意思決定を自律実行する、ゼロコストプロトタイプ

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-49%20passed-brightgreen)](#テスト)
[![Ruff](https://img.shields.io/badge/Lint-Ruff-orange)](https://github.com/astral-sh/ruff)
[![Stack](https://img.shields.io/badge/Stack-SQLite%20%7C%20FastAPI%20%7C%20Streamlit-lightgrey)](#技術スタック)

---

## なぜ ASCT か

従来のサプライチェーンシステムは「何が起きたか」を記録するだけで、「なぜその判断をしたか」を説明できない。

ASCT は Palantir Foundry のオントロジーファーストアプローチにインスパイアされ、**イベント → シグナル → シナリオ → CEO 決定** という因果チェーンをすべてのアクションに紐付ける。専門エージェントが競合シナリオを提案し、CEOOrchestrator が信頼度スコアで解決する。人間のエスカレーションが必要なケースは自動的にフラグを立てる。

---

## アーキテクチャ

```
外部イベント (需要急増・天候・供給途絶)
        │
        ▼
   [ Event ]  ─────── 因果チェーンの起点
        │
        ▼
   [ Signal ]  ─── 型付きインパクト (SupplyGap / DemandSpike / RouteDisruption ...)
        │
        ▼
  [ RunComposer ]  ── イベント種別 → エージェント組み合わせを決定
        │
   ┌────┴────────────────────────────────┐
   ▼          ▼            ▼            ▼
DemandF.  SupplyRisk  InvOpt.    LogisticsP.
(需要予測) (供給リスク) (在庫最適化) (物流計画)
   └────────────────────┬───────────────┘
                        │ Scenario[]
                        ▼
              [ CEOOrchestrator ]
              ┌─────────┴─────────┐
              ▼                   ▼
        CEODecision        EscalationRecord
        (自律実行)          (人間レビュー待ち)
```

---

## 主な特徴

- **型付きシグナル** — エージェント間を流れるデータはすべて `dimension / delta / target / confidence` を持つ。生の数値は渡さない。
- **完全な因果チェーン** — Event から Decision まで全ステップを DB に記録し、非技術者にも日本語で説明可能。
- **プラグイン型エージェント** — `BaseAgent` を継承してディレクトリに置くだけで自動登録。既存コードの変更ゼロ。
- **信頼度ゲーティング** — データ鮮度・手動入力・腐敗率から信頼スコアを動的計算。閾値未満は自動エスカレーション。
- **日本語 NL 設定パーサー** — 「欠品リスクを最優先にして」などの自然文を YAML に変換。LLM 不使用・ゼロコスト。
- **ゼロコストスタック** — SQLite / FastAPI / Streamlit / YAML のみ。クラウド課金なし。

---

## クイックスタート

```bash
# 1. 依存関係インストール
pip install -e ".[dev]"

# 2. DB マイグレーション + シードデータ生成
alembic upgrade head
python -m src.seed.generate

# 3. API サーバー起動
uvicorn src.main:app --reload
```

| サービス | URL |
|---|---|
| API (FastAPI) | http://127.0.0.1:8000 |
| ヘルスチェック | http://127.0.0.1:8000/health |
| Swagger UI | http://127.0.0.1:8000/docs |
| ダッシュボード | http://127.0.0.1:8501 |

Streamlit ダッシュボードを別途起動:

```bash
streamlit run src/dashboard.py
```

---

## API 概要

| メソッド | エンドポイント | 説明 |
|---|---|---|
| `POST` | `/api/events` | イベントを作成しエージェントパイプラインを実行 |
| `GET` | `/api/decisions` | CEO 決定一覧 |
| `GET` | `/api/decisions/{id}` | 決定詳細 + 因果チェーン |
| `GET` | `/api/escalations/pending` | 人間レビュー待ちエスカレーション |
| `PUT` | `/api/escalations/{id}/resolve` | エスカレーション解決 |
| `GET` | `/api/dashboard/status` | ダッシュボード集計データ |
| `POST` | `/api/config/parse-nl` | 日本語設定文を YAML に変換 |

---

## ディレクトリ構成

```
ASCT/
├── src/
│   ├── agents/          # プラグイン型専門エージェント (4体)
│   ├── orchestrator/    # CEOOrchestrator・RunComposer・信頼度計算・エスカレーション
│   ├── models/          # SQLAlchemy ORM (オントロジー層)
│   ├── config/          # YAML ローダー・バリデーター・日本語 NL パーサー
│   ├── api/             # FastAPI ルートモジュール
│   ├── seed/            # 決定論的シードデータ生成
│   └── dashboard.py     # Streamlit ダッシュボード
├── configs/
│   ├── company_1.yaml   # Freshfield Foods (食品・生鮮)
│   └── company_2.yaml   # NexTech Components (電子部品)
├── tests/               # pytest テストスイート (49 テスト)
├── docs/                # 設計ドキュメント (vision / decisions / state)
└── migrations/          # Alembic マイグレーション
```

---

## テスト

```bash
# 静的解析 + 型検査 + テスト
ruff check src/ tests/
pyright src/
pytest
```

| チェック | 期待結果 |
|---|---|
| Ruff | 0 issues |
| Pyright | 0 errors |
| Pytest | 49 passed |

---

## オントロジーモデル

| 種別 | 型 | 説明 |
|---|---|---|
| プリミティブ | `Asset` | 在庫・車両・サプライヤー |
| プリミティブ | `Location` | 倉庫・工場・配送センター |
| プリミティブ | `Event` | 台風・需要急増・供給途絶 |
| 派生 | `Signal` | イベントの型付きインパクト。`type / dimension / delta / target / confidence` を持つ |
| 派生 | `Action` | CEO 決定またはヒト解決済みエスカレーション |

---

## 技術スタック

| レイヤー | 採用技術 | 理由 |
|---|---|---|
| DB | SQLite + SQLAlchemy | ゼロセットアップ、外部キー強制 |
| API | FastAPI | 高速・型安全・自動ドキュメント |
| UI | Streamlit | Python のみ、最速のダッシュボード構築 |
| 設定 | YAML + ルールベース NL | LLM 不使用でゼロコスト |
| テスト | pytest + Ruff + Pyright | 静的+動的品質保証 |
| マイグレーション | Alembic | スキーマ変更の追跡 |

---

## 設計フェーズ

| フェーズ | 内容 | 状態 |
|---|---|---|
| Phase 1 | スキーマ + Alembic マイグレーション | ✅ 完了 |
| Phase 2 | シードデータ生成 | ✅ 完了 |
| Phase 3 | 専門エージェント × 4 | ✅ 完了 |
| Phase 4 | CEO オーケストレーター + エスカレーション | ✅ 完了 |
| Phase 5 | 設定レイヤー + 日本語 NL パーサー | ✅ 完了 |
| Phase 6 | FastAPI + Streamlit ダッシュボード | ✅ 完了 |

---

## ライセンス

[MIT](LICENSE)
