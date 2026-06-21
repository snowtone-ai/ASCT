# 4-3 SQLの基礎 — データベースへの命令文

> ORM の裏で動いている SQL の基本を、最小限だけ学びます。
> 「ORMのコードが、裏でどんなSQLになっているか」が想像できるようになるのがゴール。

---

## 🔵 SQL の4大命令（CRUD）

DB操作は、突き詰めると4種類です。頭文字をとって **CRUD（クラッド）** と呼びます。

| 操作 | SQL | 日本語 | ASCTのORM |
|---|---|---|---|
| Create（作成） | `INSERT` | 新しい行を追加 | `db.add(...)` |
| Read（読取） | `SELECT` | 行を取ってくる | `db.query(...)` |
| Update（更新） | `UPDATE` | 既存の行を書き換え | 属性に代入して `commit` |
| Delete（削除） | `DELETE` | 行を消す | `db.query(...).delete()` |

🟣 ASCT で一番よく出るのは **SELECT（読取）** です。エージェントが判断材料を集めるのに使います。

---

## 🔵 SELECT 文の読み方

SELECT は「どの列を・どの表から・どんな条件で」取ってくるかを書きます。

```sql
SELECT quantity_sold        -- ① どの列を：売上数量を
FROM sales_history          -- ② どの表から：売上履歴テーブルから
WHERE product_id = 5        -- ③ どんな条件で：商品IDが5のものだけ
  AND date >= '2026-05-06'; -- ④ 追加条件：この日付以降
```

🔴 **4つの部品**：
- `SELECT 列名` … 取り出す列（`*` なら全列）
- `FROM 表名` … どの表から
- `WHERE 条件` … 絞り込み条件（`AND` で複数つなげる）
- （他に `ORDER BY`＝並べ替え、`SUM()`＝合計 などがある）

---

## 🔵 集計関数 SUM — 合計を出す

ASCT は売上の合計をよく計算します。SQL では `SUM()` を使います。

```sql
SELECT SUM(quantity_sold)   -- 売上数量の合計を
FROM sales_history
WHERE product_id = 5
  AND date >= '2026-05-06'
  AND date < '2026-05-12';  -- 指定期間の
```

🟣 **実務での意味**：これは `3-6` の「直近7日の売上合計」を出すクエリそのものです。
バイヤーが「先週この商品いくつ売れた？」と聞くのを、SQL にするとこうなります。

---

## 🔵 JOIN — 複数の表をつなぐ

データは複数の表に分かれて保存されています（`events`、`companies`、`products`…）。
それらを **つなげて** 取り出すのが `JOIN` です。

```sql
SELECT inventory_policies.reorder_point, products.category
FROM inventory_policies
JOIN products ON inventory_policies.product_id = products.id   -- 商品IDで2表をつなぐ
WHERE products.category = 'fresh_produce';
```

🔵 「在庫方針」表と「商品」表を、商品IDをカギにして連結し、カテゴリで絞っています。
🟣 これは `3-6` の `query_policies` がやっていることに近い操作です（ORMでは `.join()` と書く）。

---

## 🔵 なぜ ORM があるのに SQL を学ぶのか

ASCT は ORM を使うので、普段は SQL を直接書きません。でも SQL を知っておくと：

1. **ORM のコードが何をするか想像できる**：`db.query(Event).filter_by(company_id=1)` を見て
   「裏で `SELECT * FROM events WHERE company_id=1` だな」と読める。
2. **遅いコードに気づける**：何度もDBに問い合わせる無駄なコードを見抜ける（`4-4`で触れる）。
3. **AIのDB操作を検証できる**：AIが生成したクエリが「本当に意図した行を取るか」を確かめられる。

---

## ✅ 検証ポイント

- ✅ **WHERE の抜け**：条件を書き忘れると、全件取得・全件更新・全件削除になる。
  特に `DELETE` や `UPDATE` で `WHERE` 抜けは **大事故**。AIコードで最も危険なパターンの1つ。
- ✅ **期間の境界**：`>= 開始 AND < 終了` のように、端の含む/含まないが正しいか。
  `3-6` も `>= start, < end` と、重複しないよう設計されている。
- ✅ **JOIN の条件**：`ON ...` のつなぐ列が正しいか。間違うと無関係な行同士が結合され、変な結果になる。

---

## 🧭 次へ

実際に ASCT のコードの中の SQL（ORM）クエリを読んでみましょう。→ `4-4`
