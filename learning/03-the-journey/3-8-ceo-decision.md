# 3-8 CEOの最終判断 — ceo.py を読む

> 旅の終着点にして山場。各エージェントの打ち手を見比べ、最終決定を下す「社長」のロジック。
> 対象ファイル：`src/orchestrator/ceo.py`（全91行）

---

## 🟣 このファイルの役割

**CEOオーケストレーター**。エージェントが出した打ち手（シナリオ）を受け取り、
①制約チェック → ②点数づけ → ③最終決定 を行います。
決めきれなければ **エスカレーション**（人間へ）。背骨⑥（→ `2-1`）。

---

## 🟢 心臓部：resolve メソッド（13〜30行目）

```python
def resolve(
    self, scenarios: list[dict], event: Event, config: dict
) -> CEODecision | EscalationRecord:                          # 🔴 決定 か エスカレーション を返す（1-6で予習済）
    if should_escalate_low_confidence(scenarios, event, config):  # 🔴① 緊急なのに自信不足なら…
        return create_escalation(self.session, "low_confidence", event, scenarios, config)  # 人間へ
    viable = [s for s in scenarios if check_constraints(s, config)]  # 🔴② 制約を満たす案だけ残す
    if not viable:                                            # 🔴③ 1つも残らなければ…
        return create_escalation(self.session, "no_viable_action", event, scenarios, config)  # 人間へ
    ranked = sorted(viable, key=lambda item: score_scenario(item, config))  # 🔴④ 点数の低い順に並べる
    if is_ambiguous(ranked, config):                          # 🔴⑤ 上位2案が僅差なら…
        return create_escalation(self.session, "ambiguous_recommendation", event, ranked[:2], config)  # 人間へ
    return create_decision(self.session, ranked[0], scenarios, event, config)  # 🔴⑥ 最良案を採用！
```

🔴 **この6ステップが ASCT の意思決定そのもの**。`2-1` で予告した「3つのエスカレーション理由」が、
①③⑤として実装されているのが見えます。

---

## 🔵 ステップを物語で

> **①「緊急なのに、全案の自信が低い」** → 危ないので人間へ（`low_confidence`）。
> **②「制約（予算・輸送費・最低信頼度）を満たす案だけ選別」** — ふるい落とし。
> **③「ふるいに全部落ちた」** → 打てる手が無い。人間へ（`no_viable_action`）。
> **④「残った案を、点数の低い順（＝コストが小さく望ましい順）に並べる」**
> **⑤「1位と2位の点差が小さすぎる」** → 甲乙つけ難い。人間へ（`ambiguous_recommendation`）。
> **⑥「ここまで来たら、堂々の1位を採用」** → CEODecision（決定）。

🟣 **実務での意味**：人間の役員会議の進め方そのものです。
「自信が無い案は却下」「予算オーバーは論外」「僅差なら独断せず上に諮る」。
あなたの企画思想「説明可能で、暴走しない自動意思決定」が、この6行に結晶しています。

---

## 🟢 点数のつけ方：score_scenario（33〜40行目）

```python
def score_scenario(scenario: dict, config: dict) -> float:
    weights = config["weights"]                          # 🟢 会社ごとの重み
    return round(
        weights["stockout"] * scenario["stockout_cost"]   # 🔴 欠品コスト × 重み
        + weights["holding"] * scenario["holding_cost"]    # 🔴 在庫コスト × 重み
        + weights["transport"] * scenario["transport_cost"],  # 🔴 輸送コスト × 重み
        4,
    )
```

🔵 各コストに **会社ごとの重み** を掛けて合計します（company_1.yaml では stockout:0.45, holding:0.25, transport:0.30）。
点数が **低いほど良い**（コストが小さい）。だから④で `sorted`（昇順）して1位＝最良としています。

🟣 **実務での意味**：重みは「何を一番重視するか」の経営判断です。
欠品を何より避けたい会社は `stockout` の重みを上げる。`3-6` でエージェントが出した各コストが、
ここで会社の価値観（重み）と掛け合わされ、1つの点数になります。**設定YAMLを変えれば判断が変わる** わけです。

---

## 🟢 制約チェック：check_constraints（43〜49行目）

```python
def check_constraints(scenario: dict, config: dict) -> bool:   # 🔵 OKならTrue/NGならFalse
    constraints = config["constraints"]
    if scenario["confidence"] < constraints["min_confidence"]:   # 🔴 信頼度が最低ライン未満→NG
        return False
    if scenario["total_cost"] > constraints["max_budget_jpy"]:   # 🔴 予算オーバー→NG
        return False
    return scenario["transport_cost"] <= constraints["max_transport_cost_jpy"]  # 🔴 輸送費上限以内ならOK
```

🔵 3つの関門（最低信頼度・予算・輸送費）を全部くぐれた案だけ `True`。
`resolve` の②で、この関数が `True` を返す案だけが `viable` に残ります。

---

## 🟢 僅差判定：is_ambiguous（61〜67行目）

```python
def is_ambiguous(ranked: list[dict], config: dict) -> bool:
    if len(ranked) < 2:                                  # 🟡 案が1つなら比較不能→僅差ではない
        return False
    threshold = config["escalation"]["ambiguity_threshold"]   # 🟢 僅差とみなす閾値(例:0.05)
    best = score_scenario(ranked[0], config)             # 🟢 1位の点数
    second = score_scenario(ranked[1], config)           # 🟢 2位の点数
    return abs(second - best) <= max(best, 1.0) * threshold   # 🔴 差が小さければTrue(僅差)
```

🔵 1位と2位の点差を、1位の点数の `threshold`（5%）と比べます。
差が5%以内なら「どっちも大差ない＝独断は危険」と判断し、`resolve`⑤でエスカレーション。

---

## 🟢 決定を記録：create_decision（70〜91行目）

最良案が決まったら、`CEODecision`（決定の記録）を作ってDBに保存します。
注目は `rationale`（決定理由）と `causal_chain`（なぜこの判断に至ったかの因果の鎖）を残している点：

```python
rationale="Lowest weighted scenario that satisfies constraints.",   # 🔴 決定理由を文字で残す
causal_chain={                                                       # 🔴 判断の経緯を記録
    "event_id": event.id,
    "event_type": event.event_type.value,
    "selected_scenario": selected["name"],
},
```

🟣 **実務での意味**：これが「**説明可能なAI**」の核心です。
ただ決めるだけでなく「なぜそう決めたか」を必ず記録に残す。後から人間が監査できる。
あなたの企画で最も重要な価値の1つが、この数行に実装されています。

---

## ✅ 検証ポイント

- ✅ **エスカレーション条件の順序**：①低信頼→②制約→⑤僅差 の順。順序が変わると挙動が変わる。
  例えば制約チェックより先に僅差判定すると、予算オーバーの案で僅差判定してしまう。順序の意図を読む。
- ✅ **`sorted` の向き**：点数は「低いほど良い」。昇順(`sorted`はデフォルト昇順)で1位を採るのが正しい。
  もし「高いほど良い」と取り違えて `ranked[0]` を採ると、**最悪の案を選ぶ** 重大バグになる。
- ✅ **空・1件のケア**：`is_ambiguous` の `if len(ranked) < 2` のように、件数が少ないときの処理があるか。
- ✅ **決定理由を残しているか**：`rationale` や `causal_chain` のような監査情報。
  これが無いAI判断は「なぜそうした？」に答えられず、検証不能になる。

---

## 🎉 旅の終わり

お疲れさまでした。`3-2` でイベントを受け取ってから、ここでCEOが決定を下すまで、
1件のイベントが ASCT を旅する全行程を追い切りました。

もう一度 `2-1` の地図を開いて、①〜⑧を **自分の言葉で** たどってみてください。
すべてのファイルが地図のどこに対応するか、見えるはずです。

次は、この旅のあちこちで出てきた「DBから取ってくる」「DBに保存する」の正体、
**データベースとSQL** を学びます。→ `04-database-and-sql/4-1`
