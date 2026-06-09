# chatgpt-export-search

**Search your ChatGPT history from the command line.** ChatGPT still has no real way to search your
old conversations — but you can export them all (**Settings → Data controls → Export data**), which
emails a ZIP containing `conversations.json`. This script searches every message in that file and
shows ranked matches with context, so you can finally find that thing you figured out weeks ago.

```bash
python3 chatgpt_export_search.py conversations.json "vector index"
```

```
2 message(s) match "vector index" — top 2:

  Vector DB choice  (2024-05-29, You, 1×)
    Which vector index should I use for semantic search, HNSW or IVFFlat?

  Vector DB choice  (2024-05-29, ChatGPT, 1×)
    For most apps an HNSW vector index gives the best recall/speed tradeoff.
```

- ✅ ✅ Accepts the raw export **.zip** or the extracted `conversations.json`

No dependencies — Python 3 standard library only; runs entirely locally
- ✅ Regex queries, case-insensitive, ranked by match count, with highlighted snippets
- ✅ `--role user` / `--role assistant` to search only your side or ChatGPT's
- ✅ Handles both the modern (mapping-tree) and older (flat) export formats

## Want more than keyword search?

This does local keyword/regex search, which covers a lot. If you want **semantic** search (find by
meaning, not just exact words), the ability to **ask questions** answered from your own history with
citations, and your **ChatGPT + Claude + Gemini** archives searchable together in one place, that's
exactly what **[Backscroll](https://backscroll.xyz)** does — upload the same export and go. And to
grab a single conversation without the full export, there's
**[AI Chat Exporter](https://petescribe5.gumroad.com/l/tbnxg)**.

## Part of a small suite of ChatGPT-export tools
- [chatgpt-export-to-markdown](https://github.com/jelonman/chatgpt-export-to-markdown) — turn your export into readable Markdown
- [chatgpt-export-stats](https://github.com/jelonman/chatgpt-export-stats) — wrapped-style stats from your history
- [chatgpt-export-search](https://github.com/jelonman/chatgpt-export-search) — search your history from the CLI

## License

MIT — do whatever you like.
