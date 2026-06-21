# 4-1 ORMとは何か — Pythonとデータベースの通訳

> 旅の中で何度も出てきた「DBから取ってくる」「DBに保存する」の正体を学びます。
> 対象ファイル：`src/database.py`（全16行）と概念の理解

---

## 🔵 まずデータベースとは

🔵 **データベース (DB)** は、データを表（テーブル）の形で整理して保存しておく倉庫です。
Excel のシートをイメージしてください。「行」が1件1件のデータ、「列」が項目です。

ASCT の `events` テーブルのイメージ：

| id | event_type | priority | company_id |
|----|------------|----------|------------|
| 1  | demand_spike | emergency | 1 |
| 2  | weather_event | emergency | 1 |

ASCT は **SQLite** という、ファイル1個(`asct.db`)で完結する軽量DBを使っています。

---

## 🔵 SQL と ORM

DBに「データをくれ」「保存しろ」と命じる専用言語が **SQL** です。例：

```sql
SELECT * FROM events WHERE company_id = 1;   -- 会社1のイベントを全部取ってこい
```

でも、Python の中で毎回こういう文字列を書くのは大変だし間違えやすい。
そこで **ORM** の出番です。

🔴 **ORM (Object-Relational Mapping)** とは：
**DBの「表」を、Pythonの「クラス・オブジェクト」として扱えるようにする通訳** です。

ORM を使うと、SQL を書く代わりに Python らしく書けます：

```python
# SQLを書く代わりに…
db.query(Event).filter_by(company_id=1).all()   # 会社1のEventを全部取得
```

🟣 **実務での意味**：`3-2` で見た `db.add(event)` は、裏で
`INSERT INTO events (...) VALUES (...)` という SQL に翻訳されています。
ORM のおかげで、あなたは SQL を意識せずコードを読めるのです。ASCT は **SQLAlchemy** という ORM を使っています。

---

## 🟢 database.py を読む（接続の設定）

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./asct.db"          # 🔴 DBの場所：このフォルダのasct.dbファイル

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})  # 🔵 DBへの接続口を作る
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)       # 🔵 会話窓口の製造機


@event.listens_for(engine, "connect")          # ⚪ 接続するたびに下を実行
def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
    dbapi_connection.execute("PRAGMA foreign_keys=ON")   # 🟡 外部キー制約を有効化（データの整合性を守る設定）


class Base(DeclarativeBase):                    # 🔴 全モデルの「共通の親」。4-2で使う
    pass
```

**重要な3つ**：
- `DATABASE_URL = "sqlite:///./asct.db"` … DBの場所。環境構築で作った `asct.db` がこれ。
- `SessionLocal` … 「会話窓口（Session）を作る製造機」。`3-2`の `db` はここから生まれます（`deps.py`経由）。
- `Base` … 次のレッスンで、全モデル（Event, CEODecision など）がこの `Base` を継承します。

🟡 `autocommit=False` に注目。「自動では確定しない」設定です。だから `3-3` で明示的に
`session.commit()` する必要がありました。「いつ確定するかを自分で制御する」設計です。

---

## 🔵 3つの基本動作を結びつける

旅の中で見たDB操作を、SQLとORMで対応させます：

| やりたいこと | ORM（コード中の書き方） | 裏のSQL |
|---|---|---|
| 保存する | `db.add(event)` | `INSERT` |
| 取ってくる | `db.query(Event).filter_by(...)` | `SELECT` |
| 確定する | `db.commit()` | （変更を本確定） |
| ID採番だけ先に | `db.flush()` | （まだ確定せず送る） |

---

## ✅ 検証ポイント

- ✅ **commit のし忘れ**：`add` しても `commit` しないと保存されない。
  「保存したはずなのにDBに無い」ときの典型原因。`3-3` で commit があったか思い出す。
- ✅ **DBの場所**：`DATABASE_URL` がどこを指すか。本番と開発で違うDBを指すべき。
  AIが本番DBを指したまま実験コードを書く、は事故のもと。
- ✅ **外部キー制約**：`PRAGMA foreign_keys=ON` のような整合性設定があるか。
  これが無いと「存在しない会社IDのイベント」のような壊れたデータが入りうる。

---

## 🧭 次へ

`Event` や `CEODecision` という「表に対応するクラス（モデル）」は、どう書かれている？→ `4-2`
