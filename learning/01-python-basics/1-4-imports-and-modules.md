# 1-4 import とモジュール — コードを分けて、持ってくる

> このレッスンのゴール：ファイルの先頭に並ぶ `import 〜` / `from 〜 import 〜` が読めるようになる。
> これが読めると「このファイルは、どこの何を使っているか」が分かり、コードを追えるようになります。

---

## 🔵 なぜファイルを分けるのか

ASCT は38本の `.py` ファイルでできています。1本に全部書くと数千行になって、誰も読めません。
そこで **役割ごとにファイルを分け**、必要なときに「持ってくる」のです。

- 1本のファイル = **モジュール**
- フォルダにまとめたモジュール群 = **パッケージ**（例：`src/agents/` フォルダは「agentsパッケージ」）

---

## 🔵 import の2つの書き方

### 書き方A：`import モジュール名`
```python
import yaml          # 🔵 yaml という道具一式を持ってくる
```
使うときは `yaml.safe_load(...)` のように「モジュール名.機能」と書きます。

### 書き方B：`from モジュール import 必要なものだけ`
```python
from src.config.validator import validate_config   # 🔵 validator の中の validate_config だけ持ってくる
```
使うときは `validate_config(...)` と、名前だけで直接呼べます。

🔴 **読み方**：`from A import B` は「**Aという場所から、Bを持ってくる**」。
これが読めれば、`B` の定義が `A` というファイルにあると分かり、追いかけられます。

---

## 🟢 ASCT の本物のコードで見る

`src/orchestrator/run_composer.py` の冒頭（1〜8行目）：

```python
from __future__ import annotations          # ⚪ おまじない。型ヒントを書きやすくするためのもの（無視してOK）

from sqlalchemy.orm import Session          # 🔵 外部ライブラリから「Session」を持ってくる
                                            #    （DBとの会話窓口。glossary参照）
from src.agents import PluginRegistry       # 🔵 自分のagentsパッケージから「PluginRegistry」を持ってくる
from src.models import Event                # 🔵 自分のmodelsパッケージから「Event」を持ってくる
from src.orchestrator.ceo import CEOOrchestrator      # 🔵 同じorchestrator内のceo.pyから持ってくる
from src.orchestrator.escalation import create_escalation  # 🔵 escalation.pyから関数を持ってくる
```

**この冒頭だけで分かること**：
このファイル（run_composer）は、
- `PluginRegistry`（エージェント登録係）
- `CEOOrchestrator`（CEO役）
- `create_escalation`（人間に委ねる処理）

を **使う** らしい、と。つまり import を読むだけで「このファイルが誰と協力するか」が見えます。

🟣 **実務での読解術**：知らないファイルを開いたら、**まず import の行を読む**。
そこに「このファイルが頼っている相手」が全部書いてあります。
登場人物の一覧を最初に確認する、推理小説の読み方と同じです。

---

## 🔵 `src.` は何者か

`from src.agents import ...` の `src` は、ASCT のソースコードが入った一番上のフォルダの名前です。
`src.orchestrator.ceo` は「`src` フォルダ → `orchestrator` フォルダ → `ceo.py` ファイル」を
ドットでつないだ住所表記です。

```
src/                       ← src
 └ orchestrator/           ← src.orchestrator
    └ ceo.py               ← src.orchestrator.ceo
       └ class CEOOrchestrator   ← src.orchestrator.ceo.CEOOrchestrator
```

🟡 **注意**：`from src.orchestrator.ceo import CEOOrchestrator` を読んだら、
「`src/orchestrator/ceo.py` を開けば `CEOOrchestrator` の中身が見られる」と分かります。
**import は、コードの中の道案内（リンク）** だと思ってください。

---

## ✅ 検証ポイント（AIコードを読むとき）

- ✅ **使っているのに import されていない**：コード中に `Session` が出てくるのに、
  上に `import` が無ければエラー（`NameError`）。AIが import を書き忘れる典型バグ。
- ✅ **import したのに使っていない**：持ってきたのに一度も使わない行。害は少ないが、
  「本当はここで使うはずだったのでは？」というロジック漏れのサインのことがある。
- ✅ **どこから来たか**：知らない関数が出てきたら、上の import を見れば「出身ファイル」が分かる。

---

## 🧠 理解チェック

`src/api/routes_events.py` の冒頭にこうあります：

```python
from src.orchestrator.run_composer import RunComposer
```

`RunComposer` の本体（定義）は、どのファイルを開けば見られる？
（答え：`src/orchestrator/run_composer.py`。まさに前のレッスンで見たファイルです）
