# 1-2 関数 — 入力を受け取り、結果を返す手続き

> このレッスンのゴール：`def 名前(...):` で始まるかたまりが「何の処理か」読めるようになる。

---

## 🔵 関数 = 名前のついた「処理のかたまり」

同じ処理を何度も書くのは無駄です。そこで処理に名前をつけて、呼び出せるようにします。それが **関数** です。

レシピのたとえ：
- **材料**（引数）を渡す → **調理**（処理）する → **料理**（返り値）が出てくる

```python
def add_tax(price):       # 🔵「add_tax」という関数を定義。priceを受け取る
    result = price * 1.1  # 🟢 処理：1.1倍する（消費税10%）
    return result         # 🔴 結果を返す
```

この関数を使う（**呼び出す**）には：

```python
final_price = add_tax(100)   # 🟢 100を渡すと 110.0 が返ってきて final_price に入る
```

🔴 **4つの部品を見分ける**：
1. `def` … 「これから関数を定義する」の合図
2. `add_tax` … 関数の名前
3. `(price)` … 受け取る入力（**引数**）
4. `return ...` … 返す結果（**返り値**）。`return` がない関数は「何かをするが、値は返さない」。

---

## 🟡 インデント（字下げ）が「かたまり」を決める

Python では、**行頭の空白（インデント）** が「どこからどこまでが関数の中身か」を表します。
波カッコ `{}` は使いません。

```python
def greet(name):
    message = "こんにちは " + name   # ← 字下げされている＝関数の中身
    return message                    # ← これも中身
                                      
total = greet("田中")                 # ← 字下げなし＝関数の外
```

🟡 **注意**：字下げがずれると意味が変わったりエラーになります。
AIコードを読むとき「この行は字下げされている？」を意識すると、構造が見えてきます。

---

## 🟢 ASCT の本物のコードで見る

`src/config/loader.py` 全体（短いので全部読めます）：

```python
def load_company_config(company_id: int) -> dict:                 # 🔵 会社IDを受け取り、設定(dict)を返す関数
    path = CONFIG_DIR / f"company_{company_id}.yaml"              # 🟢 設定ファイルの場所を組み立てる
    if not path.exists():                                        # 🟡 もしファイルが無ければ…
        raise FileNotFoundError(f"Company config not found: {company_id}")  # 🔴 エラーを出して止める
    config = yaml.safe_load(path.read_text(encoding="utf-8"))     # 🟢 ファイルを読んで dict に変換
    errors = validate_config(config)                             # 🟢 別の関数を呼んで中身を検査
    if errors:                                                   # 🟡 もし問題があれば…
        raise ValueError("; ".join(errors))                      # 🔴 エラーを出して止める
    return config                                               # 🔴 検査を通った設定を返す
```

**この関数を一言でいうと**：「会社番号を渡すと、その会社の設定を読み込んで返す。
ファイルが無かったり中身がおかしかったら、その場でエラーにする」。

🟣 **実務での意味**：`load_company_config(1)` を呼ぶと、`configs/company_1.yaml`
（Freshfield Foods社の設定）が読み込まれます。会社ごとに「何を重視するか」を切り替える仕組みの入口です。

⚪ **補足**：`validate_config(config)` のように、関数の中から **別の関数を呼ぶ** ことができます。
関数が関数を呼び、それがまた別の関数を呼ぶ……この連鎖がプログラムの流れです。
本編（03章）では、この連鎖を1本の「旅」として追いかけます。

---

## ✅ 検証ポイント（AIコードを読むとき）

- ✅ **入力と出力が宣言通りか**：`-> dict` と書いてあるのに、途中で数字を返していないか。
- ✅ **エラー処理があるか**：`load_company_config` のように「無かったら／おかしかったら」を
  ちゃんと処理しているか。AIコードはここを省略しがちで、それがバグの温床になります。
- ✅ **`return` を忘れていないか**：結果を返すはずの関数に `return` が無いと、呼び出し側で `None`（空）になる。

---

## 🧠 理解チェック

`src/main.py` の最後にある、この小さな関数は何を返す？

```python
@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

（ヒント：`@app.get(...)` は次章で説明します。今は `health` 関数が何を返すかだけ考えてください。）
