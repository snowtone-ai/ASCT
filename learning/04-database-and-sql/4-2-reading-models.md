# 4-2 モデルの読み方 — 表の設計図を読む

> DBの「表」に対応する Python クラス（モデル）の読み方を学びます。
> 対象ファイル：`src/models/event.py`、`src/models/base.py`

---

## 🔵 モデル = 表の設計図

🔵 **モデル (Model)** とは、DBの1つの表に対応する Python クラスです。
- クラス `Event` ＝ 表 `events`
- クラスの「属性」＝ 表の「列」
- そのクラスのインスタンス1つ ＝ 表の「1行」

`3-2` で `event = Event(...)` と作ったあの実物が、`events` 表の1行になるわけです。

---

## 🟢 Event モデルを読む（event.py 41〜58行目）

```python
class Event(ModelMixin, Base):                     # 🔵 Eventモデル。ModelMixinとBaseを継承
    __tablename__ = "events"                        # 🔴 対応する表の名前は "events"

    event_type: Mapped[EventType] = mapped_column(  # 🔵 列：event_type。種類を表す
        Enum(EventType, values_callable=enum_values), nullable=False  # 🟡 必須(nullable=False=空不可)
    )
    description: Mapped[str] = mapped_column(String(500), nullable=False)  # 🔵 列：説明（最大500文字・必須）
    priority: Mapped[EventPriority] = mapped_column(...)   # 🔵 列：優先度
    data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)  # 🔵 列：付随データ(JSON)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=False)  # 🔴 列：会社への参照

    company: Mapped[Company] = relationship(back_populates="events")   # 🟣 関連：所属する会社
    signals: Mapped[list[Signal]] = relationship(back_populates="event")  # 🟣 関連：このイベントの信号たち
    agent_decisions: Mapped[list[AgentDecision]] = relationship(...)   # 🟣 関連：エージェント判断たち
    ceo_decisions: Mapped[list[CEODecision]] = relationship(...)       # 🟣 関連：CEO決定たち
    escalations: Mapped[list[EscalationRecord]] = relationship(...)    # 🟣 関連：エスカレーションたち
```

---

## 🔵 列の定義を読む4つの部品

`event_type: Mapped[EventType] = mapped_column(...)` を分解します：

1. `event_type` … 列（属性）の名前
2. `Mapped[EventType]` … 型ヒント（1-6）。「中身は EventType」。`Mapped[...]`は「DB列ですよ」の印
3. `mapped_column(...)` … 「これはDBの列だ」という宣言と、その細かい設定
4. 設定の中身：
   - `nullable=False` … 🔴 **空(NULL)を許さない＝必須**。`3-2`で必須だった理由はここ。
   - `String(500)` … 文字列で最大500文字
   - `default=dict` … 指定されなければ空の辞書

🔴 **`nullable=False` は超重要**：これがコード(モデル)と `3-2`(API)を結びつけます。
モデルで「必須」と定めた列は、APIで `payload["..."]`（必須読み取り）になっている。
**DB設計とAPI実装が一致しているか** を、この観点で検証できます。

---

## 🟣 relationship — 表と表のつながり

`company: Mapped[Company] = relationship(...)` のような行は **列ではなく「関連」** です。
「このイベントは、どの会社に属し、どんな信号・判断を持つか」という **他の表とのつながり** を表します。

🟣 **実務での意味**：これのおかげで、コードで `event.company`（このイベントの会社）や
`event.ceo_decisions`（このイベントへのCEO判断一覧）と、表をまたいで自然にたどれます。
`3-6` の `policy.product.category` のように **ドットで関連をたどる** のは、この relationship のおかげです。

---

## 🟢 共通の親 ModelMixin（base.py 22〜32行目）

`Event` は `ModelMixin` を継承していました。その中身：

```python
class ModelMixin:
    id: Mapped[int] = mapped_column(primary_key=True)          # 🔴 全モデル共通：ID（主キー）
    created_at: Mapped[datetime] = mapped_column(..., default=utc_now)  # 🔵 作成日時（自動）
    updated_at: Mapped[datetime] = mapped_column(..., onupdate=utc_now) # 🔵 更新日時（自動）
    source: Mapped[SourceType] = mapped_column(..., default=SourceType.MANUAL)  # 🔵 情報源
```

🔵 すべてのモデルが共通で持つべき列（ID・作成日時・更新日時・情報源）を、ここにまとめています。
継承（3-5）の活用：各モデルでこれらを毎回書かずに済みます。
- `primary_key=True` … 🔴 その表の中で **1行を一意に識別する番号**。`3-2`の `db.flush()` で採番されるのがこのID。

---

## ✅ 検証ポイント

- ✅ **モデルとAPIの整合**：モデルで `nullable=False`（必須）の列が、APIで必須として扱われているか。
  ずれていると「DBは必須なのにAPIは省略可」で、保存時にエラーになる。
- ✅ **`__tablename__` の一致**：複数モデルが同じ表名を指していないか。
- ✅ **ForeignKey の正しさ**：`ForeignKey("companies.id")` の参照先が実在する表・列か。
  間違うと関連がたどれない。
- ✅ **関連の向き**：`back_populates` で双方向が一致しているか（Event.company と Company.events が対応）。

---

## 🧭 次へ

モデル（表の設計図）が読めました。次は、その表からデータを「取ってくる」SQLの基礎。→ `4-3`
