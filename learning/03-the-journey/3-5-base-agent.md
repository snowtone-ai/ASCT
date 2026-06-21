# 3-5 エージェントの設計図 — base.py を読む

> 4人のエージェントが「共通して守る約束」を定めたファイル。継承という考え方を学びます。
> 対象ファイル：`src/agents/base.py`（全30行）

---

## 🟣 このファイルの役割

すべてのエージェントの **共通の設計図（親クラス）**。
「エージェントを名乗るなら、最低限これを備えていなさい」というルールブックです。

---

## 🔵 まず「継承」を理解する

🔵 **継承 (inheritance)** とは、「ある設計図をベースに、それを引き継いだ別の設計図を作る」こと。

たとえ話：「乗り物」という親の設計図に「走る」機能があるとします。
「車」も「バイク」もこの「乗り物」を継承すれば、わざわざ書かなくても「走る」を持てます。
そして各々が自分の個性（車はドア4枚、バイクは2輪）を足します。

ASCT では：
- **親**：`BaseAgent`（このファイル）= 全エージェント共通のルール
- **子**：`DemandForecaster`、`InventoryOptimizer` など4人 = 個別の専門家

子は `class DemandForecaster(BaseAgent):` のように、カッコ内に親を書いて継承します。

---

## 🟢 全文を読む

```python
class Scenario(TypedDict):          # 🔵 「打ち手(シナリオ)」が持つべきキーの形を定義
    name: str                       # 🟢 打ち手の名前
    stockout_cost: float            # 🟢 欠品コスト
    holding_cost: float             # 🟢 在庫保持コスト
    transport_cost: float           # 🟢 輸送コスト
    total_cost: float               # 🟢 合計コスト
    confidence: float               # 🔴 信頼度(0〜1)


class BaseAgent(ABC):               # 🔴 全エージェントの親。ABC=抽象クラス（そのままでは使えない設計図）
    TRIGGERS: ClassVar[list[str]] = []   # 🔴 担当するイベント種別のリスト（子が各自で埋める）

    def __init__(self, session: Session):    # 🔵 作るとき、DB窓口を受け取る
        self.session = session               # 🔵 保管

    @property
    def name(self) -> str:                   # 🟢 エージェント名（自分のクラス名を返す）
        return self.__class__.__name__

    @abstractmethod                          # 🔴 「子は必ずこれを実装せよ」という命令
    def evaluate(self, context: dict) -> list[Scenario]:   # 🔴 打ち手を出すメソッド（中身は子が書く）
        raise NotImplementedError
```

---

## 🔵 3つの重要ポイント

### ① `Scenario` は「打ち手の形」の取り決め
`class Scenario(TypedDict):` は、「打ち手を表す辞書は、必ずこの6つのキーを持つ」という約束です。
`1-3` で見たシナリオ辞書（`demand_forecaster.py` の `return {...}`）が、ちゃんとこの形に従っています。

🔴 これが効くのは **CEO側**。CEOは `scenario["total_cost"]` のようにキーで読みます（`3-8`）。
全エージェントが同じ `Scenario` の形を守るから、CEOは「どのエージェントの打ち手も同じ方法で読める」。
**共通の様式があるから、異なる専門家の提案を横並びで比較できる** のです。

### ② `TRIGGERS` は「担当表」
`TRIGGERS: ClassVar[list[str]] = []`。親では空ですが、子がそれぞれ埋めます。
`3-4` の登録係が `event_type in agent_class.TRIGGERS` で参照していた、あの担当リストです。

### ③ `@abstractmethod` は「実装の義務」
🔴 `evaluate` に `@abstractmethod` が付いています。これは
「**BaseAgent を継承する子は、必ず自分で `evaluate` を書きなさい**」という強制です。
書き忘れたエージェントは、そもそも作れずエラーになります。

🟣 **実務での意味**：これは「品質の保証」です。
「エージェントを名乗るなら、打ち手を出す `evaluate` を必ず持て」と型で縛ることで、
中身の無いエージェントが紛れ込むのを防いでいます。`ABC`（抽象基底クラス）と `@abstractmethod` は、
そのための仕組み。`raise NotImplementedError` は「もし実装せず呼んだら、はっきりエラーにする」保険です。

---

## ⚪ 補足：`@property` と `name`

`@property` が付いた `name` は、「メソッドだけど、属性のように `()`無しで呼べる」特別な書き方。
`agent.name`（カッコ無し）で `"DemandForecaster"` のような名前が返ります。
今は「クラス名を返す便利機能」とだけ覚えてOK。

---

## ✅ 検証ポイント

- ✅ **子が `evaluate` を実装しているか**：`@abstractmethod` のメソッドを子が書き忘れると、
  そのエージェントはインスタンス化できずエラー。AIが新エージェントを書いたら、まず `evaluate` の有無を確認。
- ✅ **返り値が `Scenario` の形に従っているか**：子の `evaluate` が返す辞書が、6キーを満たしているか。
  キーが欠けると、CEO側で `scenario["holding_cost"]` がエラーになる（連鎖バグ）。
- ✅ **`TRIGGERS` が設定されているか**：空のままだと、そのエージェントはどのイベントでも選ばれない（出動しない）。

---

## 🧭 次へ

いよいよ具体的な専門家。需要予測エージェントが、どうやって打ち手を計算するのか。→ `3-6`
