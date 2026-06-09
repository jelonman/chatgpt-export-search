#!/usr/bin/env python3
"""
chatgpt_export_search.py — search your ChatGPT history from the command line.

ChatGPT has no real search for your old conversations. But you can export everything
(Settings -> Data controls -> Export data) — it emails a ZIP with `conversations.json`.
This script searches across every message in that file and shows ranked matches with
context, so you can actually find that thing you worked out weeks ago.

Usage:
    python3 chatgpt_export_search.py conversations.json "regex query"
    python3 chatgpt_export_search.py conversations.json "vector index" -n 5

No dependencies — Python 3 standard library only. Everything runs locally.
"""
import argparse
import json
import re
from datetime import datetime, timezone


import zipfile

def _load_export(path):
    """Load conversations from a ChatGPT export — accepts the raw .zip or conversations.json."""
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name = next((n for n in z.namelist() if n.endswith("conversations.json")), None)
            if not name:
                raise SystemExit("No conversations.json found inside the zip.")
            with z.open(name) as f:
                return json.loads(f.read().decode("utf-8"))
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _parts_to_text(content):
    if not isinstance(content, dict):
        return ""
    parts = content.get("parts")
    if isinstance(parts, list):
        return "\n".join((p if isinstance(p, str) else (p.get("text", "") if isinstance(p, dict) else "")) for p in parts).strip()
    return (content.get("text") or "").strip()


def _messages(convo):
    mapping = convo.get("mapping")
    rows = []
    if isinstance(mapping, dict):
        src = mapping.values()
        for node in src:
            msg = node.get("message")
            if not msg:
                continue
            role = ((msg.get("author") or {}).get("role")) or "user"
            text = _parts_to_text(msg.get("content"))
            if text and role in ("user", "assistant"):
                rows.append((role, text, msg.get("create_time")))
    else:
        for msg in convo.get("messages", []) or []:
            role = ((msg.get("author") or {}).get("role")) or msg.get("role") or "user"
            text = _parts_to_text(msg.get("content")) or (msg.get("content") if isinstance(msg.get("content"), str) else "")
            if text and role in ("user", "assistant"):
                rows.append((role, (text or "").strip(), msg.get("create_time")))
    return rows


def _snippet(text, pat, width=160):
    m = pat.search(text)
    if not m:
        return text[:width].replace("\n", " ")
    start = max(0, m.start() - width // 2)
    end = min(len(text), m.end() + width // 2)
    s = ("…" if start else "") + text[start:end].replace("\n", " ") + ("…" if end < len(text) else "")
    # highlight first match (terminal bold)
    return pat.sub(lambda mm: f"\033[1m{mm.group(0)}\033[0m", s, count=3)


def _ts(t):
    try:
        return datetime.fromtimestamp(float(t), tz=timezone.utc).strftime("%Y-%m-%d")
    except (TypeError, ValueError, OSError, OverflowError):
        return "?"


def main():
    ap = argparse.ArgumentParser(description="Search your ChatGPT conversations.json export.")
    ap.add_argument("input", help="Path to conversations.json OR the export .zip")
    ap.add_argument("query", help="Search query (treated as a regular expression; case-insensitive)")
    ap.add_argument("-n", "--num", type=int, default=10, help="Max results to show (default 10)")
    ap.add_argument("--role", choices=["user", "assistant"], help="Only search your messages or ChatGPT's")
    args = ap.parse_args()

    try:
        pat = re.compile(args.query, re.IGNORECASE)
    except re.error:
        pat = re.compile(re.escape(args.query), re.IGNORECASE)

    data = _load_export(args.input)
    convos = [c for c in (data if isinstance(data, list) else data.get("conversations", [data])) if isinstance(c, dict)]

    hits = []
    for c in convos:
        title = c.get("title") or "Untitled"
        for role, text, t in _messages(c):
            if args.role and role != args.role:
                continue
            matches = pat.findall(text)
            if matches:
                hits.append((len(matches), title, role, text, t))

    hits.sort(key=lambda h: h[0], reverse=True)
    if not hits:
        print(f'No matches for "{args.query}".')
        return
    print(f'\n{len(hits)} message(s) match "{args.query}" — top {min(args.num, len(hits))}:\n')
    for score, title, role, text, t in hits[: args.num]:
        who = "You" if role == "user" else "ChatGPT"
        print(f"  \033[36m{title}\033[0m  ({_ts(t)}, {who}, {score}×)")
        print(f"    {_snippet(text, pat)}\n")


if __name__ == "__main__":
    main()
