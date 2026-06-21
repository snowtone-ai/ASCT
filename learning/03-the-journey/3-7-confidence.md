# 3-7 信頼度の計算 — confidence.py を読む

> 「この判断、どれくらい信用していいか」を数値にする小さな（しかし重要な）ファイル。
> 対象ファイル：`src/orchestrator/confidence.py`（全23行）

---

## 🟣 このファイルの役割

各打ち手の **信頼度（0.0〜1.0）** を計算します。
信頼度は、CEOが「自動で決めるか／人間に委ねるか」を分ける重要な物差しになります（`3-8`）。

🟣 あなたの企画した「鮮度や情報源によって、判断の確からしさが変わる」という思想が、
この23行に凝縮されています。

---

## 🟢 全文を読む

```python
def calculate_confidence(
    base: float,                  # 🔵 基準となる信頼度（例:0.95）
    data_age_hours: float,        # 🔵 データの古さ（何時間前のものか）
    source: str,                  # 🔵 情報源（sensor / api / manual）
    perishability_factor: float,  # 🔵 鮮度係数（傷みやすさによる減点）
    historical_accuracy: float,   # 🔵 過去の予測精度
    config: dict,                 # 🔵 会社設定
) -> float:                       # 🔴 最終的な信頼度(0〜1)を返す
    confidence_config = config["confidence"]                    # 🟢 設定から信頼度パラメータを取り出す
    half_life_hours = confidence_config["staleness_half_life_hours"]  # 🟢 古さの半減期（食品は12時間）
    staleness_factor = 0.5 ** (data_age_hours / half_life_hours)      # 🔴 古さによる減点率
    source_multiplier = confidence_config["source_multipliers"].get(source, 0.7)  # 🔴 情報源の信頼倍率
    score = (                     # 🔴 すべてを掛け合わせる
        base
        * staleness_factor
        * source_multiplier
        * perishability_factor
        * historical_accuracy
    )
    return round(min(max(score, 0.0), 1.0), 4)   # 🔴 0〜1の範囲に収めて、小数4桁に丸める
```

---

## 🔵 計算の考え方 — 「減点方式」

基準値(`base`)から始めて、**怪しい要素を掛けて減らしていく** 方式です。
掛ける数はどれも 0〜1 なので、掛けるほど値は下がります（減点）。

### ① 古さによる減点 `staleness_factor`
```python
staleness_factor = 0.5 ** (data_age_hours / half_life_hours)
```
🔵 これは「**半減期**」の考え方。`half_life_hours`（=12時間）ごとに信頼度が半分になります。
- データが 0時間前（今）→ `0.5の0乗` = 1.0（減点なし）
- データが 12時間前 → `0.5の1乗` = 0.5（半分）
- データが 24時間前 → `0.5の2乗` = 0.25（4分の1）

🟣 **実務での意味**：「12時間前の食品在庫データは、もう半分しか信用できない」。
鮮度が命の食品サプライチェーンらしいルールです。`configs/company_1.yaml` に
`staleness_half_life_hours: 12` と書かれており、**会社ごとに変えられます**。

### ② 情報源による減点 `source_multiplier`
```python
source_multiplier = confidence_config["source_multipliers"].get(source, 0.7)
```
設定の `source_multipliers` から、情報源に応じた倍率を引きます（company_1.yaml より）：
- `sensor`（センサー実測）→ 1.0（満点。減点なし）
- `api`（外部API）→ 0.85
- `manual`（手入力）→ 0.65

🟡 `.get(source, 0.7)` の `0.7` は「もし知らない情報源だったら、とりあえず0.7」という保険（1-3で学んだ `.get` の既定値）。

### ③ 全部掛ける
`base × 古さ × 情報源 × 鮮度 × 過去精度`。1つでも低ければ、全体が大きく下がります。
「どれか1つでも怪しければ信用しない」という慎重な設計です。

### ④ 範囲に収める `round(min(max(score, 0.0), 1.0), 4)`
- `max(score, 0.0)` … 0未満なら0に（下限）
- `min(..., 1.0)` … 1超なら1に（上限）
- `round(..., 4)` … 小数4桁に丸める

🔴 この「`min(max(x, 下限), 上限)` で範囲に押し込める」形は **超頻出パターン**（クランプと呼ぶ）。
覚えておくと、いろんなコードで「ああ、0〜1に収めてるな」と即読みできます。

---

## ✅ 検証ポイント

- ✅ **範囲の保証**：信頼度は必ず0〜1であるべき。`min/max` のクランプがあるか。
  無いと、計算次第で1.2や-0.3のような「ありえない信頼度」が出て、CEOの判断を狂わせる。
- ✅ **0除算**：`data_age_hours / half_life_hours` で、`half_life_hours` が0だとエラー。
  設定値が0でないことが前提。設定の検証（validator）でガードされているか気にする。
- ✅ **掛け算の向き**：信頼を「下げる」要素なのに、うっかり足し算や割り算にすると逆効果になる。
  各係数が「0〜1で掛けて減点」という設計と整合しているか。
- ✅ **既定値の妥当性**：`.get(source, 0.7)` の 0.7 は妥当か。未知の情報源を甘く見積もりすぎていないか。

---

## 🧭 次へ

打ち手（コストと信頼度つき）が出そろいました。
いよいよCEOが、それらを見比べて最終決定する山場へ。→ `3-8`
