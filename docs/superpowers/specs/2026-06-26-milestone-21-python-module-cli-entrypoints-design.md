# Milestone 21 Python Module CLI Entrypoints Design

## Goal

Make the local CLI workflow resilient when the `llm-wiki` console script is not on `PATH` by supporting Python module execution:

- `python -m llm_wiki_core`
- `python -m llm_wiki_core.cli`

## Rationale

The primary documented user path remains the installed `llm-wiki` command. However, local Codex App / Codex CLI workflows often run inside shells where editable-install scripts or user-level script directories are not immediately discoverable. A Python module fallback improves Windows native usability without adding a new transport, service, or agent abstraction.

This is still aligned with Karpathy's LLM Wiki pattern because it only changes how the user reaches the same durable Markdown Wiki operations. It does not change the Wiki artifact model, raw source preservation, index/log/hot behavior, or artifact-level equivalence target.

## Scope

- Add package-level module execution.
- Add CLI-module execution.
- Verify both entrypoints expose version output.
- Verify the package-level module entrypoint can run the documented local workflow through subprocess boundaries.
- Document the fallback in user-facing release docs.

## Non-Goals

- Do not replace the `llm-wiki` console script.
- Do not modify global Codex configuration.
- Do not implement additional agent behavior.
- Do not modify `D:/ai/llmWiki/claude-obsidian`.
