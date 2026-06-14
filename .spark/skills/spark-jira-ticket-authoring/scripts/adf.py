#!/usr/bin/env python3
"""Build Atlassian Document Format (ADF) JSON for JIRA descriptions.

Why this exists: acli stores a plain-text description as ONE paragraph with
literal "\\n" characters. JIRA's web renderer ignores those newlines, so
headings, lists, tables, and code blocks never render — the description
collapses into a wall of text. Always send real ADF instead.

Usage:
  python3 adf.py spec.json > out.json
  acli jira workitem edit --key LEN-2 --description-file out.json --yes

spec.json is a compact block list. Each block is [kind, payload]:
  ["h",     "标题"]                                  heading (h3)
  ["p",     "段落文本"]                               paragraph
  ["ul",    ["条目1", "条目2"]]                        bullet list
  ["table", [["表头A","表头B"], ["a1","b1"], ...]]     table; first row = header
  ["code",  "自由格式\\n片段"]                         code block (snippets only)

Use tables for fixed-format content: Story acceptance criteria
(AC | Given | When | Then) and Sub-task contracts (endpoints, error codes).
Reserve "code" for free-form snippets such as a sample payload.
"""
import json
import sys


def _text(s): return {"type": "text", "text": s}
def _para(s): return {"type": "paragraph", "content": ([_text(s)] if s else [])}
def heading(s, level=3): return {"type": "heading", "attrs": {"level": level}, "content": [_text(s)]}
def paragraph(s): return _para(s)
def bullet(items): return {"type": "bulletList", "content": [{"type": "listItem", "content": [_para(i)]} for i in items]}
def code(s): return {"type": "codeBlock", "attrs": {}, "content": [_text(s)]}


def _cell(kind, s): return {"type": kind, "attrs": {}, "content": [_para(s)]}


def table(rows):
    header, *body = rows
    head = {"type": "tableRow", "content": [_cell("tableHeader", h) for h in header]}
    data = [{"type": "tableRow", "content": [_cell("tableCell", c) for c in r]} for r in body]
    return {"type": "table", "attrs": {"isNumberColumnEnabled": False, "layout": "default"}, "content": [head] + data}


_DISPATCH = {"h": heading, "p": paragraph, "ul": bullet, "table": table, "code": code}


def build(blocks):
    return {"version": 1, "type": "doc", "content": [_DISPATCH[kind](payload) for kind, payload in blocks]}


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else None
    spec = json.load(open(src, encoding="utf-8")) if src else json.load(sys.stdin)
    json.dump(build(spec), sys.stdout, ensure_ascii=False)


if __name__ == "__main__":
    main()
