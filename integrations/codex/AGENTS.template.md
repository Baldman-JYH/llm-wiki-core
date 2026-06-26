# LLM Wiki Agent Instructions

Use this vault according to the LLM Wiki pattern:

- Treat `.raw/` as immutable source material.
- Maintain `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`.
- Prefer artifact-level equivalence over byte-for-byte LLM prose matching.
- Follow the operation contracts in `docs/operation-contract.md`.

## MVP Commands

Use the local `llm-wiki` CLI when available:

- `llm-wiki init <vault> --purpose "..."`
- `llm-wiki detect-transport <vault>`
- `llm-wiki status <vault>`
- `llm-wiki continue <vault>`
- `llm-wiki ingest <vault> <source-under-.raw>`
- `llm-wiki query <vault> "<question>"`
- `llm-wiki save <vault> --title "..." --content "..."`
- `llm-wiki lint <vault>`

Natural language triggers should map to the same operations:

- "set up wiki" -> init
- "check transport" -> detect-transport
- "check wiki status" -> status
- "continue wiki" -> continue
- "resume wiki context" -> continue
- "ingest this source" -> ingest
- "what does the wiki know about X" -> query
- "save this insight" -> save
- "lint the wiki" -> lint
