# 3-1 入口 — main.py を読む

> 旅の出発点。ここで「ASCT という建物の玄関」を見ます。
> 対象ファイル：`src/main.py`（全23行。コース中いちばん短い本編ファイル）

---

## 🟣 このファイルの役割

`main.py` は ASCT サーバーの **玄関** です。
「どんな窓口（API）を備えた建物か」を宣言し、サーバー起動時に最初に読まれます。
環境構築で打った `uvicorn src.main:app` の `src.main` がこのファイル、`app` がこの中の建物本体です。

---

## 🟢 全文を読む

```python
from fastapi import FastAPI                  # 🔵 FastAPI（Web API用の道具）を持ってくる

from src.api import (                        # 🔵 自分のapiフォルダから、6つの窓口を持ってくる
    routes_company,
    routes_config,
    routes_dashboard,
    routes_decisions,
    routes_escalations,
    routes_events,                           # 🔴 今回の主役：イベント受付窓口
)

app = FastAPI(title="ASCT")                  # 🔴 「ASCT」という名前のWebアプリ本体を作る
app.include_router(routes_events.router)     # 🟢 イベント窓口を建物に取り付ける
app.include_router(routes_decisions.router)  # 🟢 決定一覧の窓口を取り付ける
app.include_router(routes_escalations.router)# 🟢 エスカレーション窓口を取り付ける
app.include_router(routes_dashboard.router)  # 🟢 ダッシュボード窓口を取り付ける
app.include_router(routes_company.router)    # 🟢 会社情報窓口を取り付ける
app.include_router(routes_config.router)     # 🟢 設定窓口を取り付ける


@app.get("/health")                          # 🔵 「/health」というURLにGETで来たら…
def health() -> dict:                        # 🟢 この関数を実行する
    return {"status": "ok"}                  # 🔴 {"status": "ok"} を返す
```

---

## 🔵 1ブロックずつの解説

**① FastAPI を持ってくる**
`from fastapi import FastAPI`。Web API を作る道具を読み込んでいます（1-4で学んだ import）。

**② 6つの窓口を持ってくる**
`from src.api import (...)`。`routes_xxx` という6つのファイルを読み込んでいます。
これらは各々が「○○用の窓口」を定義しています。今回追うのは `routes_events`（イベント受付）。

**③ アプリ本体を作る**
`app = FastAPI(title="ASCT")`。`app` という箱に、FastAPIアプリの実物を作って入れています（1-5のインスタンス）。
これが「建物本体」。`uvicorn src.main:app` の `app` はこれを指します。

**④ 窓口を取り付ける**
`app.include_router(...)` を6回。建物（app）に、6つの窓口を1つずつ取り付けています。
`app.include_router` は「app の include_router メソッド」（1-5のドット）。

**⑤ 動作確認用の窓口**
`@app.get("/health")` は「`/health` というURLにアクセスが来たら、下の関数を動かす」という指示。
中身は `{"status": "ok"}` を返すだけ。サーバーが生きているか確かめる用です。
環境構築でブラウザから叩けます：`http://localhost:8000/health`。

---

## 🔵 `@app.get(...)` の正体（デコレータ）

`@` で始まる行を **デコレータ** と呼びます。今は深入りせず、こう読んでください：

> 🔴 `@app.get("/health")` の真下の関数は、「`/health` にGETで来たときに動く窓口」になる。

`GET` は「データを取りに行く」アクセス、`POST` は「データを送り込む」アクセス。
次の `3-2` で出てくるイベント受付は `@router.post(...)`、つまり「送り込む」窓口です。

🟣 **実務での意味**：ブラウザのアドレスバーにURLを打つのが GET。
フォームに入力して「送信」を押すのが POST、というイメージです。

---

## ✅ 検証ポイント

- ✅ **取り付け忘れ**：窓口ファイルを作っても、`app.include_router(...)` を書き忘れると、
  その窓口は使えない。「APIを作ったのに404で見つからない」ときの典型原因。
- ✅ **玄関は薄いか**：良い `main.py` は「取り付けるだけ」で、複雑なロジックを持たない。
  ここに業務ロジックが書かれていたら設計が乱れているサイン。ASCT は綺麗に薄い。

---

## 🧭 次へ

玄関を見ました。次は主役の窓口、`routes_events.py` に入ります。
「イベントを1件受け取ってから何が起こるか」の旅が、いよいよ始まります。→ `3-2`
