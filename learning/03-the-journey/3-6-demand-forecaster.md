# 3-6 需要予測エージェント — demand_forecaster.py を読む

> 実際に「打ち手」を計算する専門家。本コースで一番中身の濃いファイルです。
> 対象ファイル：`src/agents/demand_forecaster.py`（全87行）。焦らず、ブロックごとに。

---

## 🟣 このファイルの役割

**需要予測の専門家**。「需要急増」「季節変動」イベントを担当し、
過去の売上から需要の傾向を読み、在庫不足のリスクを見積もって打ち手（シナリオ）を出します。背骨⑤。

---

## 🟢 クラス本体を読む（13〜22行目）

```python
class DemandForecaster(BaseAgent):                          # 🔵 BaseAgentを継承（3-5の子）
    TRIGGERS: ClassVar[list[str]] = ["demand_spike", "seasonal_change"]  # 🔴 担当イベント2種

    def evaluate(self, context: dict) -> list[Scenario]:    # 🔴 親が義務付けた「打ち手を出す」メソッド
        event: Event = context["event"]                     # 🟢 渡された箱からイベントを取り出す
        config: dict = context["config"]                    # 🟢 設定を取り出す
        target = event.data.get("target")                   # 🟢 対象カテゴリ（例:"fresh_produce"）
        policies = query_policies(self.session, event.company_id, target)  # 🟢 関係する在庫方針をDBから取得
        scenarios = [self.build_scenario(policy, config) for policy in policies]  # 🔴 各方針について打ち手を作る
        return scenarios[:2]                                # 🟡 先頭2件だけ返す
```

**読み解き**：
- `TRIGGERS` に `demand_spike` があるので、`3-4` の登録係はこのエージェントを需要急増で選びます。
- `evaluate` は `context`（イベントと設定が入った辞書）を受け取り、まず中身を取り出します。
- `query_policies(...)` でDBから関連する「在庫方針」を取得（SQLは4章で詳説。今は「DBから取ってくる」でOK）。
- 各方針について `build_scenario` で打ち手を1件ずつ作り、リストにまとめます（リスト内包表記、1-3）。
- `return scenarios[:2]` … `[:2]` は「先頭2件まで」を意味する **スライス**。多すぎる打ち手を絞っています。

---

## 🟢 打ち手を組み立てる build_scenario（24〜40行目）— このファイルの心臓

```python
def build_scenario(self, policy: InventoryPolicy, config: dict) -> Scenario:
    recent, previous = sales_windows(self.session, policy)   # 🟢 直近7日と、その前7日の売上を取得
    trend = (recent - previous) / max(previous, 1.0)         # 🔴 伸び率（増えてれば+、減ってれば-）
    inventory = query_inventory(self.session, policy)        # 🟢 今の在庫数を取得
    gap = max(policy.reorder_point - inventory.quantity, 0.0)  # 🔴 発注点に対する不足分（マイナスは0に）
    trend_pressure = max(trend, 0.0) * max(recent, 1.0)      # 🟢 上昇傾向による追加需要圧
    stockout_cost = round((gap + trend_pressure) * 1500, 2)  # 🔴 欠品コスト＝(不足+需要圧)×1500円
    holding_cost = round(max(inventory.quantity - policy.max_stock, 0.0) * 120, 2)  # 🔴 余剰在庫コスト
    confidence = calculate_policy_confidence(policy, inventory, config)  # 🔴 信頼度を計算(3-7へ)
    return {                                                 # 🔴 6キーのScenario辞書を返す(3-5の形)
        "name": f"forecast_{policy.product.category}_{policy.location.name}",
        "stockout_cost": stockout_cost,
        "holding_cost": holding_cost,
        "transport_cost": 0.0,
        "total_cost": round(stockout_cost + holding_cost, 2),
        "confidence": confidence,
    }
```

---

## 🔵 計算ロジックを「日本語の物語」に翻訳

このメソッドは、こう考えています：

1. **需要は伸びている？** … 直近7日(`recent`)と前7日(`previous`)を比べて伸び率(`trend`)を出す。
   `(recent - previous) / previous`。例：前週100→今週130なら trend は +0.3（30%増）。
2. **在庫は足りてる？** … 発注点(`reorder_point`＝補充すべきライン)と現在庫の差(`gap`)を見る。
   足りていれば（在庫>発注点）`max(..., 0.0)` で 0 になる。
3. **欠品したらいくら損？** … 不足分と需要圧を足し、1500円/単位 をかけて欠品コストに。
4. **抱えすぎてもいくら損？** … 在庫が上限(`max_stock`)を超えた分に120円/単位 をかけて保持コストに。
5. **この見立て、どれくらい自信ある？** … 信頼度を計算（次の `3-7`）。
6. **全部まとめて打ち手にする** … 6つのキーを持つ辞書（`Scenario`）にして返す。

🟣 **実務での意味**：これは人間のバイヤーが頭の中でやっている見積もりを、数式にしたものです。
「最近売れ行きが伸びてて、在庫も発注点を切ってる。今補充しないと欠品して大損だ」——
この勘を、`stockout_cost` という数字に変換しているのです。

🟡 **`max(previous, 1.0)` の意味**：もし前週売上が 0 だと、割り算 `÷0` でエラーになります。
それを防ぐため「最低でも1.0で割る」という安全策。**0除算を避ける定石**です。覚えておくと他でも見抜けます。

---

## 🟢 残りの補助関数（ざっと）

- `query_policies`（43〜48行目）… DBから在庫方針を最大5件取得。`target` があればそのカテゴリに絞る。
- `sales_windows`（51〜57行目）… 「直近7日」「その前7日」の売上合計を返す。
  🟡 ここに `today = date(2026, 5, 12)` という **固定日付** が登場（環境構築で触れた通り、練習データに合わせた意図的な固定）。
- `sales_sum`（60〜71行目）… 指定期間の売上を合計するSQL。4章で読みます。
- `calculate_policy_confidence`（82〜87行目）… 信頼度計算の入口。次の `3-7` へ。

---

## ✅ 検証ポイント

- ✅ **0除算ガード**：`max(previous, 1.0)` のような割る数の保護があるか。AIが忘れると、
  特定データで突然クラッシュする。
- ✅ **マイナスの握りつぶし**：`max(gap, 0.0)` は「不足がマイナス（＝在庫十分）なら0扱い」。
  この意図が正しいか。負のコストが混じると、後のCEOの点数計算が狂う。
- ✅ **返り値が `Scenario` の6キーを満たすか**（`3-5`の約束）。1つでも欠けるとCEO側で連鎖エラー。
- ✅ **マジックナンバー**：`1500` や `120` のような直書きの数字（マジックナンバー）。
  意味が説明されているか、設定に出すべきでないか。読むときは「この数字は何円の根拠？」と問う癖を。

---

## 🧭 次へ

`confidence = calculate_policy_confidence(...)` の中、信頼度はどう計算される？→ `3-7`
