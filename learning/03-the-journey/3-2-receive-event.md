# 3-2 イベントを受け取る — routes_events.py を読む

> 旅の本当の出発点。外から来たイベントを受け取り、処理を起動する窓口です。
> 対象ファイル：`src/api/routes_events.py`（全31行）

---

## 🟣 このファイルの役割

「需要が急増した」などのイベントを **外部から受け取る窓口**。
受け取ったら、データベースに記録し、司令塔（RunComposer）に処理を依頼し、結果を返します。
**背骨②と③の入口**（→ `2-1` の地図）。

---

## 🟢 中心部分を読む（12〜25行目）

```python
@router.post("")                              # 🔵 /api/events にPOSTで来たら、この関数を動かす
def create_event(payload: dict, db: DbSession) -> dict:   # 🔵 送られたデータ(payload)とDB窓口(db)を受け取る
    event = Event(                            # 🔴 受け取ったデータから Event の実物を組み立てる
        event_type=EventType(payload["event_type"]),       # 🟢 種類（例：demand_spike）
        description=payload.get("description", payload["event_type"]),  # 🟢 説明文（無ければ種類名を流用）
        priority=EventPriority(payload.get("priority", "scheduled")),   # 🟡 優先度（無ければ"scheduled"）
        data=payload.get("data", {}),         # 🟢 付随データ（無ければ空の辞書）
        company_id=payload["company_id"],     # 🔴 どの会社のイベントか（必須）
    )
    db.add(event)                             # 🔴 DBに「追加するよ」と予約
    db.flush()                                # 🟢 IDを確定させる（まだ完全保存ではない）
    config = load_company_config(event.company_id)   # 🟢 その会社の設定を読み込む（1-2で見た関数！）
    result = RunComposer(db).run(event, config)      # 🔴🔴 司令塔を作って、処理を実行させる
    return {"event": event_to_dict(event), "result": serialize_result(result)}  # 🟢 結果を返す
```

---

## 🔵 1行ずつ、ていねいに

**`@router.post("")`**
`/api/events` というURLに POST（データ送り込み）で来たら、下の関数が動く。`""` は「このrouterの根っこのURL」を意味し、ファイル冒頭の `prefix="/api/events"` と合わさって `/api/events` になります。

**`def create_event(payload: dict, db: DbSession) -> dict:`**
受け取るもの2つ：
- `payload: dict` … 外から送られてきたデータ（辞書）。`{"event_type": "demand_spike", "company_id": 1, ...}` のような中身。
- `db: DbSession` … DBとの会話窓口。FastAPI が自動で用意してくれる（仕組みは `deps.py`。今は「自動で来る」でOK）。

返すもの：`-> dict`、結果の辞書。

**`event = Event(...)`**
受け取った `payload`（辞書）から、`Event` クラスの実物を組み立てています（1-5のインスタンス生成）。
各項目を `payload["..."]` や `payload.get("...")` で取り出して詰めています。

🟡 **`payload["x"]` と `payload.get("x", 既定値)` の違い**（超重要）：
- `payload["event_type"]` … キーが**必ずある前提**。無ければエラーで止まる。
- `payload.get("priority", "scheduled")` … キーが**無くてもOK**。無ければ第2引数 `"scheduled"` を使う。

→ つまり `event_type` と `company_id` は **必須**、`description`・`priority`・`data` は **任意**、と
コードが語っています。この区別を読めるのが「コードを読める」ということです。

**`db.add(event)` → `db.flush()`**
`add` は「これを保存予定リストに入れる」、`flush` は「いったんDBに送ってIDを採番させる」。
まだ完全確定（commit）ではありません。確定は司令塔の中で行われます（`3-3`）。

**`config = load_company_config(event.company_id)`**
1-2で全文を読んだ関数です！ 会社IDから設定YAMLを読み込みます。
ここで「会社ごとの判断基準」が手に入ります。

**`result = RunComposer(db).run(event, config)`** 🔴 旅のハイライト
1. `RunComposer(db)` … 司令塔の実物を作る（1-5）。DB窓口を渡す。
2. `.run(event, config)` … その司令塔に「このイベントを、この設定で処理して」と依頼。
3. 返ってきた結果を `result` に受け取る。

この1行の先で、エージェントたちが動き、CEOが判断します。**次の `3-3` で、この `.run()` の中に潜ります。**

**`return {...}`**
処理したイベントと結果を、辞書にまとめて返します。これがAPIの応答としてブラウザに返ります。

---

## 🟢 末尾の小さな関数（28〜31行目）

```python
def serialize_result(result) -> dict:
    if result.__class__.__name__ == "CEODecision":      # 🔵 結果がCEODecision（決定）なら…
        return {"type": "decision", "data": decision_to_dict(result)}
    return {"type": "escalation", "data": escalation_to_dict(result)}  # それ以外はエスカレーション
```

🔵 これは「結果がCEOの決定なのか、エスカレーションなのかを見分けて、応答の形を整える」関数。
`2-1` で見た「2つの結末」が、ここに顔を出しています。
`result.__class__.__name__` は「その実物のクラス名（＝設計図の名前）を文字列で取り出す」書き方です。

---

## ✅ 検証ポイント

- ✅ **必須キーの扱い**：`payload["company_id"]` のような必須読み取りは、無いと500エラーになる。
  AIが「入力チェック無しでいきなり読む」コードは、不正な入力で落ちやすい。
- ✅ **flush と commit の違い**：`flush` だけで「保存した」と思い込むと誤り。確定は commit。
  ここでは司令塔側で commit される設計（`3-3`で確認）。「どこで確定するか」を追えるのが大事。
- ✅ **結果の分岐が網羅的か**：`serialize_result` は「CEODecisionか、それ以外」の2分岐。
  3種類目の結末が増えたらここも直す必要がある、という依存に気づけるか。

---

## 🧭 次へ

`RunComposer(db).run(event, config)` の中へ。司令塔は何をするのか。→ `3-3`
