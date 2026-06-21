# 1-5 クラス — データと処理をひとまとめにした設計図

> このレッスンのゴール：`class 〜:` が出てきたとき「これは設計図だ」と分かり、
> `何か.属性` や `何か.メソッド()` の形が読めるようになる。

---

## 🔵 クラス = 「たい焼きの金型」

クラスは **設計図（金型）** です。金型そのものは食べられません。
金型から作った **たい焼き（インスタンス）** が実物です。1つの金型から何個でも作れます。

```python
class Dog:                        # 🔵 「犬」という設計図
    def __init__(self, name):     # 🔵 作るときに呼ばれる初期設定。nameを受け取る
        self.name = name          # 🔵 この犬の名前を覚えておく（属性）

    def bark(self):               # 🔵 この犬ができる動作（メソッド）
        return self.name + "がワン!"
```

使う（インスタンスを作る）と：

```python
pochi = Dog("ポチ")     # 🟢 金型から「ポチ」という実物を作る
pochi.name              # → "ポチ"     （属性：データを取り出す）
pochi.bark()            # → "ポチがワン!" （メソッド：動作させる）
```

🔴 **3つの専門用語を結びつける**：
- **クラス** … 設計図（`class Dog`）
- **インスタンス／オブジェクト** … 設計図から作った実物（`pochi`）
- **`self`** … 「その実物自身」を指す。メソッドの中で自分の属性を触るのに使う

🟡 **`.`（ドット）の読み方**：`pochi.name` は「ポチ の 名前」、`pochi.bark()` は「ポチ が 吠える」。
**ドットは『の』『が』** と読むと自然です。
カッコ `()` が付いていれば動作（メソッド）、付いていなければデータ（属性）。

---

## 🟢 ASCT の本物のコードで見る

`src/orchestrator/run_composer.py` の11〜18行目。司令塔クラスです：

```python
class RunComposer:                          # 🔵「実行をまとめる係」の設計図
    def __init__(self, session: Session):   # 🔵 作るときに、DB窓口(session)を受け取る
        self.session = session              # 🔵 受け取った窓口を自分の中に保管
        self.registry = PluginRegistry(session)   # 🔵 エージェント登録係も内部に持つ
        self.ceo = CEOOrchestrator(session)       # 🔵 CEO役も内部に持つ

    def run(self, event: Event, config: dict):     # 🔵 「実行する」動作。イベントと設定を受け取る
        agents = self.registry.get_agents_for_event(event.event_type.value)  # 🟢 自分が持つregistryに仕事を頼む
        ...
```

**読み解き**：
- `RunComposer` は、作られるとき（`__init__`）に **3つの道具**（DB窓口・エージェント登録係・CEO役）を
  自分の中に抱え込みます。
- `run()` というメソッドが、実際の仕事（イベントを処理する）を担当します。
- `self.registry.get_agents_for_event(...)` は「**自分が持っている** registry **に** 仕事を頼む」。
  ドットが2つ続くのは「自分 の registry の get_agents...動作」と読みます。

🟣 **実務での意味**：`RunComposer` は、オーケストラの指揮者のような存在です。
自分では演奏（個別の判断）をしませんが、奏者（エージェント）と作曲家（CEO）を抱えていて、
イベントが来たら「君たち演奏して」「君が最終判断して」と段取りします。
本編 `3-3` でこのクラスを丸ごと読みます。

---

## ⚪ 補足：`__init__` という名前

`__init__`（アンダースコア2個ずつ）は特別な名前で、「インスタンスを作る瞬間に自動で呼ばれる関数」です。
「初期設定（initialize）」の略。`RunComposer(session)` と書くと、この `__init__` が裏で動きます。
最初は「作るときの準備係」とだけ覚えれば十分です。

---

## ✅ 検証ポイント（AIコードを読むとき）

- ✅ **`self.` を付け忘れていないか**：メソッド内で自分の属性を使うときは `self.xxx`。
  ただの `xxx` だと別物（その場limの変数）になり、バグになる。
- ✅ **`()` の有無**：データが欲しいのに `pochi.bark`（カッコ無し）と書くと、動作そのものを指してしまい
  実行されない。逆に属性に `()` を付けるとエラー。
- ✅ **`__init__` で受け取った引数を保管しているか**：受け取ったのに `self.` に入れ忘れると、
  後で使えずエラーになる。

---

## 🧠 理解チェック

`src/orchestrator/ceo.py` の9〜11行目：

```python
class CEOOrchestrator:
    def __init__(self, session: Session):
        self.session = session
```

`CEOOrchestrator` は作られるとき、何を受け取って、何を自分の中に保管している？
（答え：DBとの会話窓口 `session` を受け取り、`self.session` に保管している）
