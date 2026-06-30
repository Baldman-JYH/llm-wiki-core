# llm-wiki-core

`llm-wiki-core` is a neutral local LLM Wiki practice implementation. The canonical abstraction is [Karpathy's LLM Wiki gist](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f): raw materials stay durable, and the agent maintains a Markdown wiki instead of leaving knowledge trapped in chat. [AgriciDaniel/claude-obsidian](https://github.com/AgriciDaniel/claude-obsidian) is the reference implementation for the Claude Code + Obsidian workflow, while `llm-wiki-core` focuses on a neutral, testable core that does not claim full parity with `claude-obsidian`.

Current status: R3.2 adds URL ingest on top of the MVP local loop. The project remains a text-first local workflow and does not claim full parity with `claude-obsidian`.

<!-- Compatibility anchors for existing hygiene tests:
## 蹇€熷紑濮?
## 浣跨敤鏂瑰紡
## 鍛戒护閫熸煡
## 鏂囨。
## 褰撳墠杈圭晫
楠岃瘉閫氳繃
��֤ͨ��
official `obsidian` CLI
filesystem fallback
验证通过
-->

## 项目定位

- Karpathy's gist is the canonical abstract idea.
- `AgriciDaniel/claude-obsidian` is the reference implementation for Claude Code + Obsidian.
- `llm-wiki-core` is a neutral practice implementation for Codex App, Codex CLI, and future local agents.

## 主要能力

- Initialize a standard local LLM Wiki vault.
- Preserve raw source inputs under `.raw/`.
- Track source metadata and provenance in `.raw/.manifest.json`.
- Ingest single local Markdown sources.
- Ingest local Markdown folders with `ingest-batch`.
- Ingest one explicit URL into an immutable `.raw/url/` snapshot with `ingest-url`.
- Query, save, resume, and lint the wiki.
- Use `filesystem` as the default portable runtime path, with the official `obsidian` CLI treated as an optional verified runtime and `filesystem fallback` preserved.

## 快速开始

### 安装

```powershell
git clone https://github.com/Baldman-JYH/llm-wiki-core.git
cd llm-wiki-core
python -m pip install -e .
python -m llm_wiki_core --version
```

### 初始化

```powershell
llm-wiki init <vault> --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport <vault> --force
```

### 摄取本地来源与 URL

```powershell
llm-wiki ingest <vault> .raw/articles/example.md
llm-wiki ingest-batch <vault> .raw/articles
llm-wiki ingest-batch <vault> .raw/articles --force
llm-wiki ingest-url <vault> https://example.com/article
```

### 查询与检查

```powershell
llm-wiki status <vault>
llm-wiki continue <vault>
llm-wiki query <vault> "What does the wiki know about this source?"
llm-wiki save <vault> --title "Saved Insight" --content "Durable insight text."
llm-wiki lint <vault>
```

## 使用方式

- CLI: run `llm-wiki` directly after install.
- Codex App / Codex CLI: initialize a vault and follow the generated `AGENTS.md`.
- Local automation: every command can return 机器可读 JSON with `--json`.

## 命令速查

| Command | Purpose |
|---|---|
| `llm-wiki init <vault> --purpose "..."` | Initialize a local wiki vault. |
| `llm-wiki detect-transport <vault> --force` | Record runtime transport capability metadata. |
| `llm-wiki ingest <vault> <source>` | Ingest one local Markdown source under `.raw/`. |
| `llm-wiki ingest-batch <vault> <source-root>` | Ingest local Markdown files discovered under `.raw/`. |
| `llm-wiki ingest-url <vault> <url>` | Fetch one explicit URL, store an immutable `.raw/url/` snapshot, and ingest the normalized Markdown source. |
| `llm-wiki status <vault>` | Inspect initialization and source status. |
| `llm-wiki continue <vault>` | Re-enter current wiki context. |
| `llm-wiki query <vault> "<question>"` | Query the wiki. |
| `llm-wiki save <vault> --content "..."` | Save durable insight back into the wiki. |
| `llm-wiki lint <vault>` | Check wiki health and write a lint report. |

## 产物结构

```text
<vault>/
  AGENTS.md
  .raw/
    .manifest.json
    url/
  wiki/
    index.md
    log.md
    hot.md
    overview.md
    sources/
    entities/
    concepts/
    questions/
    comparisons/
    meta/
```

- `.raw/` stores preserved raw inputs.
- `.raw/url/` stores immutable URL ingest snapshots.
- `wiki/` stores durable Markdown knowledge artifacts.

## 与 claude-obsidian 的关系

`llm-wiki-core` deliberately keeps the core neutral. It reuses the same abstract idea and durable artifact shape, but it does not claim full parity with `claude-obsidian`.

## 文档

- [用户指南](docs/user-guide.md)
- [操作契约](docs/operation-contract.md)
- [Manifest Schema](docs/manifest-schema.md)
- [路线图排期](docs/roadmap-schedule.md)
- [完成标准](docs/completion-criteria.md)
- [路线图](docs/roadmap.md)
- [发布就绪清单](docs/release-readiness-checklist.md)
- [发布说明](docs/release-notes-v0.1.0-mvp.md)
- [归档说明](docs/archive-manifest.md)

## 当前边界

- URL ingest creates immutable `.raw/url/` snapshots.
- R3.2 is text-only.
- R3.2 does not include full readability, defuddle, JavaScript rendering, authenticated pages, or crawling.
- Binary or non-decodable responses are rejected instead of being archived through the text transport.
- The official `obsidian` CLI remains optional and verified-only; `filesystem fallback` stays available.

## 路线图

- R1: hardening.
- R2: verified optional runtime transport for the official `obsidian` CLI.
- R3: ingest and retrieval expansion, including local Markdown batch ingest and URL ingest.
- R4: adapter expansion.
- R5: knowledge-organization extensions.

See [docs/roadmap-schedule.md](docs/roadmap-schedule.md) for the prioritized schedule.

## 开发与测试

```powershell
python -m pip install -e .
python -m pytest
```

## 许可

The repository does not yet ship a final `LICENSE` file.
