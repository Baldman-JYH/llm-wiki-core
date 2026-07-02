# Codex Command Mapping

This document maps Codex App / CLI natural language triggers to local `llm-wiki` commands. Natural language triggers are required; slash commands are a target UX layer.

| Natural language trigger | Target slash command | CLI command | Mutation behavior | Key files |
|---|---|---|---|---|
| set up wiki | `/wiki` | `llm-wiki init <vault> --purpose "..."` | writes vault scaffold | `AGENTS.md`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| scaffold vault | `/wiki` | `llm-wiki init <vault> --purpose "..."` | writes vault scaffold | `AGENTS.md`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| check transport | `/wiki transport` | `llm-wiki detect-transport <vault>` | writes transport snapshot | `wiki/meta/transport.json` |
| check wiki status | `/wiki status` | `llm-wiki status <vault>` | read-only | `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| continue wiki | `/wiki` | `llm-wiki continue <vault>` | read-only | `wiki/hot.md`, `wiki/index.md`, `wiki/log.md` |
| resume wiki context | `/wiki` | `llm-wiki continue <vault>` | read-only | `wiki/hot.md`, `wiki/index.md`, `wiki/log.md` |
| ingest this source | `/wiki ingest <source>` | `llm-wiki ingest <vault> <source-under-.raw>` | writes wiki artifacts | `.raw/.manifest.json`, `wiki/sources/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| ingest this folder | `/wiki ingest-batch <source-root>` | `llm-wiki ingest-batch <vault> <source-root>` | writes wiki artifacts | `.raw/.manifest.json`, `wiki/sources/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| ingest this URL | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` | writes raw snapshot and wiki artifacts | `.raw/url/`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| search wiki for X | `/wiki search <query>` | `llm-wiki search <vault> "X"` | read-only | `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/questions/`, `wiki/comparisons/` |
| find wiki pages about X | `/wiki search <query>` | `llm-wiki search <vault> "X"` | read-only | `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/questions/`, `wiki/comparisons/` |
| what does the wiki know about X | `/wiki query <question>` | `llm-wiki query <vault> "X"` | read-only | `wiki/hot.md`, `wiki/index.md`, ranked wiki pages |
| save this insight | `/wiki save [title]` | `llm-wiki save <vault> --title "..." --content "..."` | writes wiki artifact | `wiki/questions/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
| lint the wiki | `/wiki lint` | `llm-wiki lint <vault>` | writes lint report | `wiki/meta/`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |
