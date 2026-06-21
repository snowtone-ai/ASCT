# 3-4 エージェント自動登録 — agents/__init__.py を読む

> 「イベントの種類に合う担当者を自動で選ぶ」仕掛けを見ます。ASCT で最も賢い部分のひとつ。
> 対象ファイル：`src/agents/__init__.py`（全41行）

---

## 🟣 このファイルの役割

**登録係（PluginRegistry）**。
`agents/` フォルダに置かれたエージェントを **自動で発見** し、
イベントの種類に応じて「対応できる担当者」だけを選んで返します。背骨④（→ `2-1`）。

🟣 **なぜ嬉しいか**：新しいエージェントを足したいとき、`agents/` にファイルを1つ置くだけで、
**他のどこも書き換えずに** 自動で認識されます。あなたの企画 D-001「ゼロ改変でエージェント追加」の心臓部です。

---

## 🟢 PluginRegistry クラスを読む（11〜32行目）

```python
class PluginRegistry:
    def __init__(self, session: Session):
        self.session = session
        self._agent_classes: list[type[BaseAgent]] = []   # 🔵 発見したエージェント設計図を貯める箱（最初は空）

    def discover(self) -> list[type[BaseAgent]]:          # 🔴 エージェントを自動発見するメソッド
        if self._agent_classes:                          # 🟢 既に発見済みなら…
            return self._agent_classes                   #     もう一度探さず、それを返す（節約）
        package_name = __name__                          # 🔵 自分のパッケージ名（"src.agents"）
        for module_info in pkgutil.iter_modules(__path__):  # 🔴 agentsフォルダ内の各.pyファイルを順に見る
            if module_info.name == "base" or module_info.name.startswith("_"):  # 🟡 baseと_始まりは除外
                continue                                 #     （baseは設計図、_は裏方なのでスキップ）
            module = importlib.import_module(f"{package_name}.{module_info.name}")  # 🟢 そのファイルを読み込む
            self._agent_classes.extend(find_agent_classes(module))  # 🟢 中のエージェントを箱に追加
        return self._agent_classes                       # 🔴 発見した全エージェントを返す

    def get_agents_for_event(self, event_type: str) -> list[BaseAgent]:  # 🔴 イベントに合う担当を選ぶ
        return [
            agent_class(self.session)                    # 🟢 合致したエージェントの実物を作って…
            for agent_class in self.discover()           #    全エージェントの中から
            if event_type in agent_class.TRIGGERS        # 🔴 そのイベント種別を担当するものだけ
        ]
```

---

## 🔵 2つのメソッドの役割

### `discover()` — 「どんなエージェントがいるか、自動で名簿を作る」

普通なら、エージェントを増やすたびに「このエージェントも登録して」とリストに手書きします。
ASCT はそれをしません。`discover()` が **フォルダの中を自分で見て回り**、名簿を自動生成します。

- `pkgutil.iter_modules(__path__)` … 「`agents/` フォルダの中の `.py` ファイルを1つずつ列挙する」道具。
- `base` と `_`始まりを除外 … `base.py` は設計図そのもの、`__init__.py` は裏方なので名簿に入れない。
- `importlib.import_module(...)` … ファイルを動的に読み込む。
- `find_agent_classes(module)` … そのファイルの中から「エージェントの設計図」を拾う（下記）。

🟡 `if self._agent_classes: return ...` は **キャッシュ**。一度名簿を作ったら、次回は作り直さず使い回す節約です。

### `get_agents_for_event(event_type)` — 「イベントに合う担当だけ選ぶ」

名簿（`discover()`の結果）の中から、`event_type in agent_class.TRIGGERS` を満たすものだけを選びます。

🔴 **ここが核心**：各エージェントは `TRIGGERS`（担当するイベント種別のリスト）を持っています（次の `3-5`）。
`"demand_spike" in agent_class.TRIGGERS` は「このエージェントの担当リストに demand_spike が含まれるか」。
含まれるものだけ実物化して返す。**だから需要急増には需要予測担当だけが出動する** のです。

---

## 🟢 補助関数 find_agent_classes（35〜40行目）

```python
def find_agent_classes(module: object) -> list[type[BaseAgent]]:
    classes = []
    for item in vars(module).values():           # 🟢 ファイル内の全要素を1つずつ見る
        if isinstance(item, type) and issubclass(item, BaseAgent) and item is not BaseAgent:  # 🔴 条件
            classes.append(item)                 # 🟢 条件を満たすものだけ集める
    return classes
```

🔵 条件 `isinstance(item, type) and issubclass(item, BaseAgent) and item is not BaseAgent` は、
「それはクラスで、かつ BaseAgent を継承していて、かつ BaseAgent 自身ではない」という意味。
つまり「**本物のエージェント設計図だけ**を拾う」フィルターです（継承は `3-5` で説明）。

---

## 🟣 全体の動きを物語で

> イベント「需要急増(demand_spike)」が来た。
> 司令塔が登録係に「担当は誰？」と聞く（`3-3`①）。
> 登録係は初めてなので `agents/` フォルダを見回り、4人のエージェントを発見して名簿を作る（`discover`）。
> 名簿から「TRIGGERSに demand_spike を含む人」を探すと、需要予測担当(`DemandForecaster`)が該当。
> その1人だけを司令塔に返す。

---

## ✅ 検証ポイント

- ✅ **除外条件の正しさ**：`base` や `_`始まりを除外し忘れると、設計図そのものを
  エージェントとして動かそうとしてエラーになる。ここは正しく除外している。
- ✅ **該当ゼロのケース**：もしどのエージェントの TRIGGERS にも無いイベント種別が来たら、
  `get_agents_for_event` は **空リスト** を返す。→ 司令塔の `3-3`③（打ち手ゼロ→エスカレーション）に繋がる。
  「該当なしのとき何が返るか」を追えるのが重要。
- ✅ **自動発見の副作用**：「フォルダに置けば自動で動く」は便利な反面、
  間違ったファイルを置くと勝手に読み込まれる。動的読み込みは強力ゆえ注意が要る、と意識する。

---

## 🧭 次へ

各エージェントが持つ `TRIGGERS` や `evaluate()` は、どこで定義されている？
すべてのエージェントの「設計図の親玉」、`base.py` へ。→ `3-5`
