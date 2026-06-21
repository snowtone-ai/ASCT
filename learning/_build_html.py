# -*- coding: utf-8 -*-
"""
learning/ の教材Markdown(01〜04)を、色分けが視覚的に見えるHTMLに変換するツール。

使い方（プロジェクト直下で）:
    python learning/_build_html.py

- 01〜04 ディレクトリ内の *.md を、同じ場所に *.html として書き出す。
- 各HTMLはCSSを内蔵した自己完結ファイル。ダブルクリックでブラウザで開ける。
- 色マーク（🔵🟢🟡🔴🟣✅⚪）で始まる行は、対応する色の囲みボックスになる。
- Markdownを編集したら、このスクリプトを再実行すれば全HTMLが作り直される。
"""
from __future__ import annotations

import html
import re
from pathlib import Path

LEARNING_DIR = Path(__file__).resolve().parent
TARGET_DIRS = ["01-python-basics", "02-big-picture", "03-the-journey", "04-database-and-sql"]

# 色マーク -> (CSSクラス名, 表示ラベル)
COLOR_MARKS = {
    "🔵": ("c-blue", "概念"),
    "🟢": ("c-green", "コード"),
    "🟡": ("c-yellow", "注意"),
    "🔴": ("c-red", "重要"),
    "🟣": ("c-purple", "実務"),
    "✅": ("c-check", "検証"),
    "⚪": ("c-gray", "補足"),
    "🧠": ("c-brain", "理解チェック"),
    "🎓": ("c-grad", "まとめ"),
}

CSS = """
:root { color-scheme: light dark; }
* { box-sizing: border-box; }
body {
  font-family: "Yu Gothic", "Hiragino Kaku Gothic ProN", "Meiryo", system-ui, sans-serif;
  line-height: 1.9; color: #1f2328; background: #f6f7f9;
  margin: 0; padding: 2rem 1rem; -webkit-text-size-adjust: 100%;
}
.wrap { max-width: 820px; margin: 0 auto; background: #fff;
  padding: 2.4rem 2.6rem; border-radius: 14px;
  box-shadow: 0 1px 3px rgba(0,0,0,.08), 0 8px 24px rgba(0,0,0,.05); }
h1 { font-size: 1.7rem; line-height: 1.4; margin: .2em 0 .8em;
  padding-bottom: .4em; border-bottom: 3px solid #2563eb; }
h2 { font-size: 1.35rem; margin: 1.8em 0 .6em; padding-left: .5em;
  border-left: 6px solid #2563eb; }
h3 { font-size: 1.12rem; margin: 1.4em 0 .5em; color: #0f3b8c; }
p { margin: .7em 0; }
a { color: #2563eb; }
hr { border: 0; border-top: 1px dashed #cbd5e1; margin: 1.8em 0; }
code { font-family: "Cascadia Code", Consolas, "Courier New", monospace;
  background: #eef1f5; padding: .12em .4em; border-radius: 5px; font-size: .92em; }
pre { background: #0f172a; color: #e2e8f0; padding: 1rem 1.1rem; border-radius: 10px;
  overflow-x: auto; line-height: 1.65; font-size: .9rem; }
pre code { background: none; padding: 0; color: inherit; font-size: inherit; }
pre .lang { display: block; font-size: .72rem; letter-spacing: .08em;
  color: #94a3b8; text-transform: uppercase; margin-bottom: .5rem; }
blockquote { margin: 1em 0; padding: .6em 1.1em; color: #475569;
  background: #f1f5f9; border-left: 5px solid #94a3b8; border-radius: 0 8px 8px 0; }
blockquote p { margin: .3em 0; }
table { border-collapse: collapse; width: 100%; margin: 1.1em 0; font-size: .94rem; }
th, td { border: 1px solid #d8dee4; padding: .55em .8em; text-align: left; vertical-align: top; }
th { background: #eef2ff; }
ul, ol { margin: .6em 0; padding-left: 1.5em; }
li { margin: .3em 0; }
strong { color: #b91c1c; }

/* 色マークの囲みボックス */
.callout { margin: .7em 0; padding: .7em 1em .7em 1em; border-radius: 0 8px 8px 0;
  border-left: 6px solid; position: relative; }
.callout .tag { display: inline-block; font-size: .72rem; font-weight: 700;
  padding: .05em .55em; border-radius: 999px; margin-right: .5em; vertical-align: .12em; color:#fff; }
.callout ul, .callout ol { margin: .3em 0; }
.c-blue   { background:#eff6ff; border-color:#3b82f6; }  .c-blue .tag{background:#3b82f6;}
.c-green  { background:#ecfdf5; border-color:#10b981; }  .c-green .tag{background:#10b981;}
.c-yellow { background:#fffbeb; border-color:#f59e0b; }  .c-yellow .tag{background:#d97706;}
.c-red    { background:#fef2f2; border-color:#ef4444; }  .c-red .tag{background:#ef4444;}
.c-purple { background:#faf5ff; border-color:#a855f7; }  .c-purple .tag{background:#a855f7;}
.c-check  { background:#f0fdf4; border-color:#22c55e; }  .c-check .tag{background:#16a34a;}
.c-gray   { background:#f8fafc; border-color:#94a3b8; }  .c-gray .tag{background:#64748b;}
.c-brain  { background:#fdf4ff; border-color:#c026d3; }  .c-brain .tag{background:#c026d3;}
.c-grad   { background:#fffbeb; border-color:#eab308; }  .c-grad .tag{background:#ca8a04;}
.legend { display:flex; flex-wrap:wrap; gap:.4em; margin:.4em 0 1.4em; font-size:.78rem; }
.legend span { padding:.15em .6em; border-radius:999px; color:#fff; }
.nav { font-size:.85rem; color:#64748b; margin-bottom:1.4em; }
@media (prefers-color-scheme: dark) {
  body { background:#0b1020; color:#e5e7eb; }
  .wrap { background:#121829; box-shadow:none; }
  h3 { color:#93c5fd; } code { background:#1e293b; color:#e2e8f0; }
  th { background:#1e293b; } td, th { border-color:#334155; }
  blockquote { background:#1a2132; color:#cbd5e1; }
  strong { color:#fca5a5; }
  .c-blue{background:#13203a;}.c-green{background:#0c2a22;}.c-yellow{background:#2a2410;}
  .c-red{background:#2a1518;}.c-purple{background:#241433;}.c-check{background:#0c2a1a;}
  .c-gray{background:#1a2132;}.c-brain{background:#26122b;}.c-grad{background:#2a2410;}
}
"""

INLINE_CODE_RE = re.compile(r"`([^`]+)`")
BOLD_RE = re.compile(r"\*\*([^*]+)\*\*")


def render_inline(text: str) -> str:
    """インライン要素（`code` と **bold**）をHTMLに。先にコードを退避して二重処理を防ぐ。"""
    placeholders: list[str] = []

    def stash(m: re.Match) -> str:
        placeholders.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(placeholders) - 1}\x00"

    text = INLINE_CODE_RE.sub(stash, text)
    text = html.escape(text)
    text = BOLD_RE.sub(r"<strong>\1</strong>", text)
    for i, ph in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", ph)
    return text


def detect_color(text: str):
    """行頭の色マークを検出し (クラス, ラベル, マーク文字) を返す。無ければNone。"""
    stripped = text.lstrip()
    for mark, (cls, label) in COLOR_MARKS.items():
        if stripped.startswith(mark):
            return cls, label, mark
    return None


def convert(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # フェンスコードブロック
        if line.lstrip().startswith("```"):
            lang = line.lstrip()[3:].strip()
            i += 1
            buf: list[str] = []
            while i < n and not lines[i].lstrip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # 閉じる ```
            code = html.escape("\n".join(buf))
            label = f'<span class="lang">{html.escape(lang)}</span>' if lang else ""
            out.append(f"<pre>{label}<code>{code}</code></pre>")
            continue

        # 見出し
        if line.startswith("### "):
            out.append(f"<h3>{render_inline(line[4:])}</h3>")
            i += 1
            continue
        if line.startswith("## "):
            out.append(f"<h2>{render_inline(line[3:])}</h2>")
            i += 1
            continue
        if line.startswith("# "):
            out.append(f"<h1>{render_inline(line[2:])}</h1>")
            i += 1
            continue

        # 水平線
        if line.strip() == "---":
            out.append("<hr>")
            i += 1
            continue

        # テーブル
        if line.strip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2  # ヘッダ + 区切り
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table>", "<thead><tr>"]
            t += [f"<th>{render_inline(c)}</th>" for c in header]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{render_inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue

        # 引用
        if line.lstrip().startswith(">"):
            buf = []
            while i < n and lines[i].lstrip().startswith(">"):
                buf.append(render_inline(lines[i].lstrip()[1:].lstrip()))
                i += 1
            out.append("<blockquote>" + "".join(f"<p>{b}</p>" for b in buf if b) + "</blockquote>")
            continue

        # リスト（- か 数字.）。各項目の色マークも判定。
        if re.match(r"^\s*([-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\s*\d+\.\s+", line))
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            while i < n and re.match(r"^\s*([-*]|\d+\.)\s+", lines[i]):
                content = re.sub(r"^\s*([-*]|\d+\.)\s+", "", lines[i])
                color = detect_color(content)
                if color:
                    cls, label, mark = color
                    body = render_inline(content.lstrip()[len(mark):].lstrip())
                    items.append(f'<li class="callout {cls}"><span class="tag">{label}</span>{body}</li>')
                else:
                    items.append(f"<li>{render_inline(content)}</li>")
                i += 1
            out.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        # 空行
        if line.strip() == "":
            i += 1
            continue

        # 段落（連続する非空・非特殊行をまとめる）
        para: list[str] = []
        while i < n and lines[i].strip() != "" and not _is_block_start(lines[i], lines, i):
            para.append(lines[i])
            i += 1
        text = " ".join(p.strip() for p in para)
        color = detect_color(text)
        if color:
            cls, label, mark = color
            body = render_inline(text.lstrip()[len(mark):].lstrip())
            out.append(f'<p class="callout {cls}"><span class="tag">{label}</span>{body}</p>')
        else:
            out.append(f"<p>{render_inline(text)}</p>")

    return "\n".join(out)


def _is_block_start(line: str, lines: list[str], i: int) -> bool:
    s = line.lstrip()
    if s.startswith(("#", ">", "```", "- ", "* ")):
        return True
    if line.strip() == "---":
        return True
    if re.match(r"^\s*\d+\.\s+", line):
        return True
    if s.startswith("|") and i + 1 < len(lines) and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
        return True
    return False


LEGEND = (
    '<div class="legend">'
    '<span style="background:#3b82f6">🔵 概念</span>'
    '<span style="background:#10b981">🟢 コード</span>'
    '<span style="background:#d97706">🟡 注意</span>'
    '<span style="background:#ef4444">🔴 重要</span>'
    '<span style="background:#a855f7">🟣 実務</span>'
    '<span style="background:#16a34a">✅ 検証</span>'
    '<span style="background:#64748b">⚪ 補足</span>'
    "</div>"
)


def wrap_html(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n"
        '<html lang="ja"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{html.escape(title)}</title>"
        f"<style>{CSS}</style></head><body>"
        f'<div class="wrap"><div class="nav">ASCT 学習教材 — このファイルはMarkdownから自動生成されています</div>'
        f"{LEGEND}{body}</div></body></html>\n"
    )


def main() -> None:
    count = 0
    for d in TARGET_DIRS:
        for md_path in sorted((LEARNING_DIR / d).glob("*.md")):
            md = md_path.read_text(encoding="utf-8")
            title_match = re.search(r"^#\s+(.+)$", md, re.MULTILINE)
            title = title_match.group(1).strip() if title_match else md_path.stem
            body = convert(md)
            html_path = md_path.with_suffix(".html")
            html_path.write_text(wrap_html(title, body), encoding="utf-8")
            count += 1
            print(f"  生成: {html_path.relative_to(LEARNING_DIR)}")
    print(f"\n完了: {count} 個のHTMLを生成しました。")


if __name__ == "__main__":
    main()
