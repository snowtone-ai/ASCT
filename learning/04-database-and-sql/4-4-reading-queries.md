# 4-4 コード中のクエリを読む — 本物のORMクエリ

> ASCT の実コードに出てくるORMクエリを読み、「裏でどんなSQLか」を想像する練習。
> 対象ファイル：`src/agents/demand_forecaster.py` の query系関数

---

## 🟢 例1：在庫を1件取ってくる（query_inventory, 74〜79行目）

```python
def query_inventory(session, policy: InventoryPolicy) -> Inventory:
    return (
        session.query(Inventory)                  # 🔵 Inventory表から
        .filter_by(product_id=policy.product_id,  # 🔴 条件：この商品で
                   location_id=policy.location_id) #        この拠点の
        .one()                                     # 🔴 ちょうど1件を取る
    )
```

🔵 **裏のSQLに翻訳すると**：
```sql
SELECT * FROM inventory
WHERE product_id = ? AND location_id = ?;
```

🔴 **`.one()` の意味**：「**ちょうど1件** あるはず」という取り方。
- 0件だったらエラー、2件以上でもエラーになります。
- 似た仲間：`.all()`（全件をリストで）、`.first()`（先頭1件、無ければNone）。

🟡 **検証の勘所**：`.one()` は「絶対1件」と断言する強い書き方。
もしデータが無い可能性があるなら `.first()` を使うべき。AIが `.one()` を安易に使い、
データ欠損時に予期せぬクラッシュ、はよくある。「ここは本当に必ず1件か？」と問う。

---

## 🟢 例2：売上を合計する（sales_sum, 60〜71行目）

```python
def sales_sum(session, policy, start, end) -> float:
    value = (
        session.query(func.coalesce(func.sum(SalesHistory.quantity_sold), 0.0))  # 🔴 売上合計（無ければ0）
        .filter(
            SalesHistory.product_id == policy.product_id,   # 🔵 この商品
            SalesHistory.location_id == policy.location_id, # 🔵 この拠点
            SalesHistory.date >= start,                     # 🔵 開始日以降
            SalesHistory.date < end,                        # 🔵 終了日より前
        )
        .scalar()                                            # 🔴 単一の値として取り出す
    )
    return float(value)
```

🔵 **裏のSQLに翻訳すると**：
```sql
SELECT COALESCE(SUM(quantity_sold), 0.0) FROM sales_history
WHERE product_id = ? AND location_id = ?
  AND date >= ? AND date < ?;
```

🔴 **2つの注目点**：
- `func.sum(...)` … `4-3` で学んだ `SUM()`。売上数量の合計。
- `func.coalesce(..., 0.0)` … 「もし合計が NULL（該当行ゼロ）なら 0.0 にする」安全策。
  売上ゼロの期間でもエラーにならず 0.0 が返る。`3-6` の trend 計算が壊れないための備え。
- `.scalar()` … 「表ではなく、1個の数値」を取り出す。合計値が1つ欲しいので。

🟣 **実務での意味**：`3-6` の `sales_windows` がこの関数を2回呼んで、
「直近7日」「その前7日」の売上を出し、需要の伸びを計算していました。
この `sales_sum` こそ、需要予測の **生データを集める井戸** です。

---

## 🟢 例3：JOIN を使う（query_policies, 43〜48行目）

```python
def query_policies(session, company_id: int, target: str | None) -> list[InventoryPolicy]:
    query = session.query(InventoryPolicy).join(InventoryPolicy.product)  # 🔴 在庫方針と商品を連結
    query = query.filter_by(company_id=company_id)                        # 🔵 この会社で絞る
    if target:                                                            # 🟡 targetが指定されていれば…
        query = query.filter_by(category=target)                         #     カテゴリでも絞る
    return query.limit(5).all()                                          # 🔴 最大5件をリストで取得
```

🔵 **裏のSQLに翻訳すると**（target指定ありの場合）：
```sql
SELECT * FROM inventory_policies
JOIN products ON inventory_policies.product_id = products.id
WHERE company_id = ? AND category = ?
LIMIT 5;
```

🔴 **注目点**：
- `.join(InventoryPolicy.product)` … `4-3` の JOIN。在庫方針と商品表をつなぐ。
- `if target:` … 条件を **動的に組み立てている**。targetがある時だけ絞り込みを追加。
  クエリを少しずつ組み上げる書き方です。
- `.limit(5)` … 最大5件まで（取りすぎ防止）。`4-3` には無かった `LIMIT`。

🟡 **検証の勘所**：`if target:` は、`target` が `None` や空文字のときカテゴリ絞りをスキップします。
これが意図通りか？ 「全カテゴリ対象」が正しい挙動か確認する。

---

## 🔴 まとめ：ORMクエリを読む手順

知らないORMクエリに出会ったら、この順で読みます：

1. **`.query(なに)`** … どの表から取るか（FROM）
2. **`.filter(...)` / `.filter_by(...)`** … どんな条件か（WHERE）
3. **`.join(...)`** … 他の表とつなぐか（JOIN）
4. **`.sum` / `.coalesce` など** … 集計や加工はあるか
5. **最後の `.one()` / `.all()` / `.scalar()` / `.first()`** … どう取り出すか（1件/全件/数値）

この5点を押さえれば、たいていのクエリは「裏のSQL」に翻訳して理解できます。

---

## ✅ 総合検証ポイント

- ✅ **取り出し方の妥当性**：`.one()`（必ず1件）か `.first()`（無いかも）か。データ欠損の可能性と合っているか。
- ✅ **NULLガード**：`coalesce` のような「該当ゼロ件」の備えがあるか。無いと後続計算が壊れる。
- ✅ **LIMIT / 件数制御**：取りすぎていないか。大量データを一度に取ると遅くなる。
- ✅ **N+1問題**（応用）：ループの中で毎回クエリを投げていないか。`3-6` のように件数を絞り、
  ループ内クエリを最小にしているか。「繰り返しの中のDB問い合わせ」は遅さの典型原因。

---

## 🎓 コース完走

ここまでで、ASCT を題材に
**Python の読み方 → 全体構造 → 1イベントの処理の旅 → DBとSQL** をひと通り歩きました。

`progress.md` のすべてに `[x]` がついたら、最後の仕上げとして
`3-2` をもう一度開き、**コードを見ずに「イベントが来てから何が起こるか」を説明** してみてください。
それができたら——あなたは「AIのコードを読んで検証できる人」です。おめでとうございます。
