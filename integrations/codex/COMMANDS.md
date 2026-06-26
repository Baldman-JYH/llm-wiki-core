# Codex Command Mapping

This document maps Codex App / CLI natural language triggers to the local `llm-wiki` MVP commands.

| Natural language trigger | CLI command |
|---|---|
| set up wiki | `llm-wiki init <vault> --purpose "..."` |
| scaffold vault | `llm-wiki init <vault> --purpose "..."` |
| check transport | `llm-wiki detect-transport <vault>` |
| check wiki status | `llm-wiki status <vault>` |
| continue wiki | `llm-wiki continue <vault>` |
| resume wiki context | `llm-wiki continue <vault>` |
| ingest this source | `llm-wiki ingest <vault> <source-under-.raw>` |
| what does the wiki know about X | `llm-wiki query <vault> "X"` |
| save this insight | `llm-wiki save <vault> --title "..." --content "..."` |
| lint the wiki | `llm-wiki lint <vault>` |

The target slash-command experience can mirror these operations later, but natural language triggers are the required MVP path.
