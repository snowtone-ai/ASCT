# 3-3 司令塔 — run_composer.py を読む

> 前回の `RunComposer(db).run(event, config)` の中に入ります。
> 対象ファイル：`src/orchestrator/run_composer.py`（全29行）

---

## 🟣 このファイルの役割

**司令塔（指揮者）**。自分では判断しませんが、
「エージェントたちに打ち手を出させ → CEOに最終判断させ → 結果を確定保存する」という
**段取り全体** を取り仕切ります。背骨③（→ `2-1`）。

---

## 🟢 全文を読む

```python
class RunComposer:
    def __init__(self, session: Session):           # 🔵 作るとき、DB窓口を受け取る
        self.session = session                      # 🔵 保管
        self.registry = PluginRegistry(session)     # 🔵 エージェント登録係を内部に持つ
        self.ceo = CEOOrchestrator(session)         # 🔵 CEO役を内部に持つ

    def run(self, event: Event, config: dict):      # 🔴 実行本体。イベントと設定を受け取る
        agents = self.registry.get_agents_for_event(event.event_type.value)  # 🔴① 担当エージェントを選ぶ
        scenarios = []                              # 🟢 打ち手を貯める空リストを用意
        for agent in agents:                        # 🔴② 選ばれた各エージェントについて…
            scenarios.extend(agent.evaluate({"event": event, "config": config}))  # 打ち手を出させて貯める
        if not scenarios:                           # 🟡③ もし打ち手が1つも出なかったら…
            result = create_escalation(             #     人間に委ねる（no_viable_action）
                self.session, "no_viable_action", event, scenarios, config
            )
        else:                                       # 🔴④ 打ち手があれば…
            result = self.ceo.resolve(scenarios, event, config)  # CEOに最終判断させる
        self.session.commit()                       # 🔴⑤ ここで初めてDBに確定保存
        return result                               # 🟢 結果を返す
```

---

## 🔵 `run()` の5ステップを追う

これが ASCT の処理の **背骨そのもの** です。番号順に。

**① 担当エージェントを選ぶ**
```python
agents = self.registry.get_agents_for_event(event.event_type.value)
```
`event.event_type.value` は、イベントの種類を文字列で取り出したもの（例：`"demand_spike"`）。
それを登録係（registry）に渡し、「この種類に対応できるエージェント一覧」を受け取ります。
**「需要急増」なら需要予測担当だけが返る** — この選別の中身は次の `3-4`。

**② 各エージェントに打ち手を出させる**
```python
scenarios = []
for agent in agents:
    scenarios.extend(agent.evaluate({...}))
```
- `scenarios = []` … 空のリストを用意（1-3）。ここに打ち手を貯めます。
- `for agent in agents:` … 選ばれたエージェントを1人ずつ処理（繰り返し）。
- `agent.evaluate({...})` … 各エージェントの「評価する」メソッドを呼ぶ。打ち手のリストが返る。
- `scenarios.extend(...)` … 返ってきた打ち手を `scenarios` に **追加して** いく。

🟡 **`append` と `extend` の違い**：`extend` はリストを「中身ごと」足し込む。
各エージェントが複数の打ち手（リスト）を返すので、それらを1つの大きなリストにまとめています。

**③ 打ち手ゼロなら、人間へ**
```python
if not scenarios:
    result = create_escalation(self.session, "no_viable_action", ...)
```
`if not scenarios:` は「もし scenarios が空なら」。打ち手が1つも出なければ、
AIには手に負えないので **エスカレーション**（人間に委ねる）。`2-1` の結末2です。

**④ 打ち手があれば、CEOへ**
```python
else:
    result = self.ceo.resolve(scenarios, event, config)
```
打ち手があれば、内部に抱えたCEO役（`self.ceo`）に「これらを見比べて決めて」と依頼。
このCEOの判断中身が、本編の山場 `3-8`。

**⑤ ここで確定保存**
```python
self.session.commit()
```
🔴 `3-2` で「確定は司令塔で」と予告した通り、**ここが commit**。
これより前の `db.add` や `db.flush` は「下書き」。`commit` で初めてDBに本保存されます。

🟣 **実務での意味**：途中でエラーが起きたら commit に到達しないので、中途半端なデータが残りません。
「全部成功したら、まとめて確定する」という安全設計（トランザクション）です。

---

## 🔵 司令塔は「自分では判断しない」

注目してほしいのは、`run()` の中に **業務的な判断（コスト計算や点数づけ）が一切ない** こと。
やっているのは「誰に頼むか」「結果をどう確定するか」という **段取りだけ**。

🔴 これは良い設計の典型です。「段取り係」と「判断係」を分けることで、
判断ロジックを変えたいときは CEO（`ceo.py`）だけ、エージェントを足したいときは `agents/` だけ、
と **触る場所が局所化** されます。あなたの企画した「エージェントを足しやすい」設計（D-001）の現れです。

---

## ✅ 検証ポイント

- ✅ **commit の位置**：commit が `if/else` の **外（共通）** にあるのが正しい。
  もし片方の分岐の中だけにあったら、もう片方で保存されないバグになる。ここでは外にあり正しい。
- ✅ **空リストの処理**：`if not scenarios:` のような「結果ゼロ件」のケアがあるか。
  AIコードはこの「0件・空・None」の処理を忘れがち。ここはちゃんとある。
- ✅ **エラー時にcommitされないか**：途中で例外が出れば commit 前に抜けるので安全。
  逆に「途中で部分的にcommitする」コードは、データが壊れる温床。

---

## 🧭 次へ

「①担当エージェントを選ぶ」の中身、`get_agents_for_event` へ。
ASCT の賢い仕掛け「自動でエージェントを見つける」を見ます。→ `3-4`
