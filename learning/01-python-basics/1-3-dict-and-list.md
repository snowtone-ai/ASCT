# 1-3 辞書とリスト — データをまとめて持つ

> このレッスンのゴール：`{...}` と `[...]` が出てきたとき、何が入っているか読めるようになる。
> ASCT のコードは「辞書」と「リスト」だらけです。ここが読めると一気に視界が開けます。

---

## 🔵 リスト `[...]` = 順番に並んだ値の列

```python
prices = [100, 200, 300]        # 🔵 3つの数を順番に並べたリスト
agents = ["DemandForecaster", "InventoryOptimizer"]  # 🔵 文字列のリスト
```

中身は **順番（インデックス）** で取り出します。番号は **0から** 始まります。

```python
prices[0]   # → 100  （0番目＝最初）
prices[2]   # → 300  （2番目＝3つ目）
```

🟡 **注意**：「1番目」が `[0]` です。日常の数え方と1つズレるので、最初は戸惑います。
「0から数える」と覚えてください。

---

## 🔵 辞書 `{...}` = 「名前：値」のペアの集まり

リストが「順番で取り出す」のに対し、辞書は **名前（キー）で取り出します**。

```python
product = {                    # 🔵 1つの商品を表す辞書
    "name": "りんご",          # キー "name" → 値 "りんご"
    "price": 100,              # キー "price" → 値 100
    "category": "fresh_produce",
}
```

中身は **キー** で取り出します：

```python
product["name"]      # → "りんご"
product["price"]     # → 100
```

🔴 **これが最重要**：ASCT では、エージェントの提案（シナリオ）も、会社の設定も、
APIで受け取るデータも、ほとんどが **辞書** で表現されています。
`なにか["キー"]` という形を見たら「辞書から値を取り出している」と即座に分かるようにしましょう。

---

## 🟢 ASCT の本物のコードで見る — シナリオは辞書

`src/agents/demand_forecaster.py` の33〜40行目。エージェントが作る「打ち手の候補（シナリオ）」です：

```python
return {                                              # 🔵 シナリオ1件を辞書で返す
    "name": f"forecast_{policy.product.category}_{policy.location.name}",  # 打ち手の名前
    "stockout_cost": stockout_cost,                   # 🟢 欠品したときの損失コスト
    "holding_cost": holding_cost,                     # 🟢 在庫を抱えるコスト
    "transport_cost": 0.0,                            # 🟢 輸送コスト
    "total_cost": round(stockout_cost + holding_cost, 2),  # 🟢 合計コスト
    "confidence": confidence,                         # 🔴 この提案への自信(0〜1)
}
```

🟣 **実務での意味**：これは「需要予測エージェントが出す1つの提案書」です。
「この打ち手だと、欠品コストはいくら、在庫コストはいくら、信頼度はこれくらい」という
見積もりが、6個のキーを持つ1つの辞書にまとまっています。

そして、この辞書を **CEOオーケストレーター** が後で読んで（`scenario["total_cost"]` のように）、
どの打ち手を採用するか決めます。`src/orchestrator/ceo.py` の36〜38行目を見てください：

```python
weights["stockout"] * scenario["stockout_cost"]    # 🟢 シナリオ辞書から欠品コストを取り出して重みをかける
+ weights["holding"] * scenario["holding_cost"]     # 🟢 在庫コストにも重みをかける
+ weights["transport"] * scenario["transport_cost"] # 🟢 輸送コストにも
```

> 🔴 つまり「エージェントが辞書を作る → CEOがその辞書を読む」。
> 辞書は、モジュール間で情報を受け渡す **共通の入れ物** なのです。

---

## 🔵 組み合わせ：辞書のリスト

実際には「シナリオが何個もある」ので、**辞書を並べたリスト** がよく出てきます。

```python
scenarios = [          # 🔵 リストの中に…
    {"name": "案A", "total_cost": 5000, "confidence": 0.9},   # 辞書
    {"name": "案B", "total_cost": 4000, "confidence": 0.7},   # 辞書
]
```

これを1件ずつ処理するのが `for`（繰り返し）です。`ceo.py` の20行目：

```python
viable = [scenario for scenario in scenarios if check_constraints(scenario, config)]
```

🔵 これは「`scenarios` の中の各 `scenario` について、`check_constraints` がOKなものだけ集めて
`viable`（実行可能な案）というリストを作る」という意味。**リスト内包表記** という書き方です（1-3では「こういう形がある」とだけ知ればOK）。

---

## ✅ 検証ポイント（AIコードを読むとき）

- ✅ **存在しないキーを読んでいないか**：辞書に無いキー `data["xxx"]` を読むとエラーになる。
  AIが「あるはず」と思い込んでアクセスして落ちる、はよくあるバグ。
- ✅ **リストの番号がはみ出ていないか**：3個のリストに `[5]` でアクセスするとエラー。
- ✅ **キー名のスペルミス**：`"confidence"` と `"confidance"` を取り違えると、別物として扱われる。

---

## 🧠 理解チェック

次の辞書から「信頼度」を取り出すには、どう書く？

```python
result = {"name": "案A", "total_cost": 4000, "confidence": 0.82}
```

（答え：`result["confidence"]` → `0.82`）
