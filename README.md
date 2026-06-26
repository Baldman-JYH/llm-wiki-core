# llm-wiki-core

`llm-wiki-core` 是一个中性核心项目，用来把 Karpathy 的 LLM Wiki pattern 落地为可由不同本地 Agent 适配的知识库维护系统。

当前阶段已完成 `v0.1.0-mvp` 本地发布收口：MVP 核心流程已经通过自动化产物等价验证，面向 Codex App / CLI 用户的本地使用指南已补齐，并明确当前状态为 MVP Local Complete；full `claude-obsidian` parity 属于后续路线图，不是 MVP 完成标准。

## 项目定位

本项目位于三层关系中的第三层：

1. **抽象思想**：Karpathy 的 LLM Wiki gist 是 canonical pattern。
2. **具体案例**：`D:/ai/llmWiki/claude-obsidian` 是该 pattern 在 Claude Code + Obsidian 场景下的参考实现。
3. **综合实践版本**：`llm-wiki-core` 计划抽象出中性核心，使 Codex App / Codex CLI 等本地 Agent 也能实现与 Claude Code 使用 `claude-obsidian` 相同的知识库维护效果。

`llm-wiki-core` 不是 `claude-obsidian` 的完整复制品，也不是对 Karpathy gist 的自由改写。它应吸收 `claude-obsidian` 已验证的实践经验，同时把 Agent 特定部分放进 adapter，让共同核心保持中性。

## 核心思想

本项目的 canonical 思想来源是 Karpathy 的 gist：<https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f>。

本地文件 `D:/ai/llmWiki/llm-wiki.md` 只是当前工作区内的参考副本。若本地副本与 Karpathy gist 存在差异，应以 Karpathy gist 为准。

本项目必须服从该 pattern 的核心思想：

- 人类负责选择来源、提出问题、判断方向。
- LLM 负责阅读、摘要、交叉链接、归档、更新索引、维护日志、发现矛盾。
- 最终产物不是聊天记录，而是持久、复利、可维护的 Markdown Wiki。

## 三层结构

- Raw sources：不可变来源材料。
- Wiki：LLM 维护的 Markdown 知识层。
- Schema：约束 LLM 如何摄取、查询、整理和维护 Wiki 的规则层。

## 当前规划目标

- 抽象出中性核心，不绑定 Claude 或 Codex。
- 首先支持本地 Codex App 与 Codex CLI。
- 以 `claude-obsidian` 的有效用户体验作为参考实现对齐目标。
- Windows 原生支持，不依赖 WSL 或 Git Bash。
- 文件系统 transport 必须可用；Obsidian CLI 可检测但在 actual read/write/search 实现前不作为 preferred runtime transport。
- 采用 artifact-level equivalence，而不是全量字节级一致。

## 当前非目标

- 不追求完整复制 `claude-obsidian` 的全部高级能力。
- 不追求所有 LLM-authored content 字节级一致。
- 不优先支持 Codex Web / Remote。
- 不自动修改全局 Codex 配置。
- 不发布 marketplace plugin。
- 不接入 MCP / REST API。
- 不做远端 Git 推送。

## 规划文档索引

- `docs/mvp-scope.md`：MVP 范围。
- `docs/capability-mapping.md`：`claude-obsidian` 能力映射。
- `docs/reference-implementation-alignment.md`：与 `claude-obsidian` 的参考实现关系。
- `docs/agent-behavioral-contract.md`：跨 Agent 行为契约。
- `docs/manifest-schema.md`：最小 manifest schema。
- `docs/generic-mode-structure.md`：generic mode 目录结构。
- `docs/codex-command-contract.md`：Codex App / CLI 命令契约。
- `docs/operation-contract.md`：core operation 输入、输出、错误模式和验证标准。
- `docs/transport-contract.md`：transport 优先级和回退契约。
- `docs/parity-testing.md`：artifact-level equivalence 验证原则。
- `docs/test-fixture-plan.md`：测试夹具计划。
- `docs/adapter-packaging-plan.md`：Codex adapter 包装计划。
- `docs/implementation-readiness-checklist.md`：进入实现阶段前的检查清单。
- `docs/project-skeleton-plan.md`：未来项目骨架计划。
- `docs/milestone-plan.md`：MVP 里程碑计划。
- `docs/mvp-review.md`：Milestone 8 MVP 复核结论。
- `docs/local-install-rehearsal.md`：Milestone 14 本地安装端到端演练记录。
- `docs/codex-adapter-install-rehearsal.md`：Milestone 15 Codex adapter 安装路径演练记录。
- `docs/obsidian-cli-transport-boundary-rehearsal.md`：Milestone 16 Obsidian CLI transport 边界演练记录。
- `docs/artifact-equivalence-verification.md`：Milestone 19 artifact-level equivalence 自动化验证报告。
- `docs/user-guide.md`：Milestone 20 本地 Codex App / CLI 用户指南。
- `docs/release-readiness-checklist.md`：Milestone 20 MVP 发布就绪检查清单。
- `docs/completion-criteria.md`：Milestone 22 MVP 完成标准。
- `docs/roadmap.md`：Milestone 22 后续路线图。
- `docs/release-notes-v0.1.0-mvp.md`：`v0.1.0-mvp` 本地发布说明。
- `docs/archive-manifest.md`：发布归档策略与校验说明。
- `docs/roadmap-schedule.md`：后续路线图排期。
- `docs/superpowers/plans/2026-06-25-milestone-1-project-skeleton.md`：Milestone 1 项目骨架实施计划。
- `docs/superpowers/specs/2026-06-25-milestone-2-init-design.md`：Milestone 2 init 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-3-transport-design.md`：Milestone 3 transport detection 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-4-ingest-design.md`：Milestone 4 single-source ingest 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-5-query-save-design.md`：Milestone 5 query/save 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-6-lint-design.md`：Milestone 6 lint 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-7-codex-adapter-design.md`：Milestone 7 Codex adapter 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-8-mvp-review.md`：Milestone 8 MVP review 设计记录。
- `docs/superpowers/specs/2026-06-25-milestone-9-transport-read-write-search-design.md`：Milestone 9 transport read/write/search 设计记录。
- `docs/superpowers/plans/2026-06-25-milestone-9-transport-read-write-search.md`：Milestone 9 transport read/write/search 实施计划。
- `docs/superpowers/specs/2026-06-25-milestone-10-operation-transport-adoption-design.md`：Milestone 10 operation transport adoption 设计记录。
- `docs/superpowers/plans/2026-06-25-milestone-10-operation-transport-adoption.md`：Milestone 10 operation transport adoption 实施计划。
- `docs/superpowers/specs/2026-06-25-milestone-11-status-continue-design.md`：Milestone 11 status / continue 设计记录。
- `docs/superpowers/plans/2026-06-25-milestone-11-status-continue.md`：Milestone 11 status / continue 实施计划。
- `docs/superpowers/specs/2026-06-25-milestone-12-codex-adapter-status-continue-design.md`：Milestone 12 Codex adapter status / continue 设计记录。
- `docs/superpowers/plans/2026-06-25-milestone-12-codex-adapter-status-continue.md`：Milestone 12 Codex adapter status / continue 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-13-installer-smoke-tests-design.md`：Milestone 13 installer smoke tests 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-13-installer-smoke-tests.md`：Milestone 13 installer smoke tests 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-14-local-install-rehearsal-design.md`：Milestone 14 local install rehearsal 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-14-local-install-rehearsal.md`：Milestone 14 local install rehearsal 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-15-codex-adapter-install-rehearsal-design.md`：Milestone 15 Codex adapter install rehearsal 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-15-codex-adapter-install-rehearsal.md`：Milestone 15 Codex adapter install rehearsal 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-16-obsidian-cli-transport-boundary-design.md`：Milestone 16 Obsidian CLI transport boundary 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-16-obsidian-cli-transport-boundary.md`：Milestone 16 Obsidian CLI transport boundary 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-17-operation-transport-consistency-design.md`：Milestone 17 operation transport consistency 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-17-operation-transport-consistency.md`：Milestone 17 operation transport consistency 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-18-ingest-save-write-transport-consistency-design.md`：Milestone 18 ingest/save write transport consistency 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-18-ingest-save-write-transport-consistency.md`：Milestone 18 ingest/save write transport consistency 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-19-artifact-equivalence-verification-design.md`：Milestone 19 artifact equivalence verification 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-19-artifact-equivalence-verification.md`：Milestone 19 artifact equivalence verification 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-20-release-readiness-user-guide-design.md`：Milestone 20 release readiness / user guide 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-20-release-readiness-user-guide.md`：Milestone 20 release readiness / user guide 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-21-python-module-cli-entrypoints-design.md`：Milestone 21 python module CLI entrypoints 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-21-python-module-cli-entrypoints.md`：Milestone 21 python module CLI entrypoints 实施计划。
- `docs/superpowers/specs/2026-06-26-milestone-22-completion-criteria-roadmap-design.md`：Milestone 22 completion criteria / roadmap 设计记录。
- `docs/superpowers/plans/2026-06-26-milestone-22-completion-criteria-roadmap.md`：Milestone 22 completion criteria / roadmap 实施计划。

## Development Status

Milestone 22 currently implements and locally verifies the MVP core loop, repo-local Codex adapter assets, neutral filesystem transport, initial operation transport adoption, read-only vault re-entry commands, Codex adapter discovery for those commands, installer dry-run smoke coverage, real editable-install CLI rehearsal, real Codex adapter installer rehearsal, Obsidian CLI transport boundary semantics, runtime transport consistency, ingest/save write-path transport consistency, automated artifact-level equivalence verification, release-readiness user documentation, Python module CLI fallback entrypoints, and completion criteria / roadmap documentation:

- Python package metadata and importable core modules.
- `init_vault()` core API.
- `llm-wiki init <vault> --purpose "..."` CLI entry.
- Generic Wiki scaffold with `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md`, `wiki/overview.md`, and required folders.
- Codex-facing `AGENTS.md` generation.
- `detect_transport()` core API.
- `llm-wiki detect-transport <vault> [--force]` CLI entry.
- `.vault-meta/transport.json` snapshot with detection and implementation state separated per transport.
- `ingest_source()` core API.
- `llm-wiki ingest <vault> <source> [--force]` CLI entry.
- Single local raw source ingest with source summary page, manifest update, index/log/hot updates, and unchanged-source skip.
- `query_wiki()` core API.
- `llm-wiki query <vault> <question>` CLI entry.
- Deterministic Wiki page search with wikilink citations and gap reporting.
- `save_insight()` core API.
- `llm-wiki save <vault> --content "..." [--title "..."] [--target-type question|concept]` CLI entry.
- Save to questions/concepts pages with index/log/hot updates.
- `lint_wiki()` core API.
- `llm-wiki lint <vault> [--no-report]` CLI entry.
- Required path, manifest JSON, frontmatter, dead wikilink, and orphan page checks.
- Stable lint report at `wiki/meta/lint-report-YYYY-MM-DD.md`.
- Codex `AGENTS.template.md`.
- Codex skill draft at `integrations/codex/skills/llm-wiki/SKILL.md`.
- Codex command mapping at `integrations/codex/COMMANDS.md`.
- PowerShell and shell install entrypoints under `integrations/codex/install/`.
- Test fixture directories.
- Codex and Claude adapter placeholder directories.
- MVP smoke test covering `init -> detect-transport -> ingest -> query -> save -> lint`.
- `FilesystemTransport` with UTF-8 `read_text`, `write_text`, `append_text`, `list_markdown`, and `search_text`.
- Transport path safety for vault-relative paths, rejecting absolute paths and traversal outside the vault.
- `query_wiki(..., transport=None)` with default filesystem transport and injectable transport for adapters/tests.
- `lint_wiki(..., transport=None)` with default filesystem transport and injectable transport for adapters/tests.
- `status_wiki(..., transport=None)` and `llm-wiki status <vault>` for read-only vault health/status summary.
- `continue_wiki(..., transport=None)` and `llm-wiki continue <vault>` for read-only hot/index/log context recovery.
- Codex adapter natural language triggers for "check wiki status", "continue wiki", and "resume wiki context".
- PowerShell installer `-DryRun`.
- shell installer `--dry-run`.
- Installer next-step hints for `llm-wiki status <vault>` and `llm-wiki continue <vault>`.
- Explicit setuptools package discovery for `llm_wiki_core*`, preventing adapter asset directories from breaking editable install.
- Lint wikilink resolution against both page file stems and frontmatter `title` values.
- Local install rehearsal proving `llm-wiki --version`, `init`, `detect-transport`, `status`, `continue`, `ingest`, `query`, `save`, and `lint` through the installed console entrypoint.
- Generated `AGENTS.md` includes Codex MVP command discovery and natural language trigger mapping.
- Codex command mapping Markdown table rows are covered by tests.
- Codex adapter installer rehearsal proving `install.ps1 -> init -> detect-transport -> status -> continue -> lint` on a temporary vault.
- Obsidian CLI detection records `available` separately from `implemented`.
- Fresh detection keeps `preferred: filesystem` while Obsidian CLI actual read/write/search is unimplemented.
- `ObsidianCliTransport` placeholder raises a clear not-implemented boundary error.
- Obsidian CLI boundary rehearsal proving detected Obsidian CLI does not override filesystem preference.
- Runtime transport selector treats snapshot preferred values as advisory metadata.
- `query`, `lint`, `status`, `continue`, `ingest`, and `save` default through runtime transport selection.
- Legacy snapshots that prefer unimplemented Obsidian CLI fall back to filesystem with warnings.
- `ingest_source(..., transport=None)` and `save_insight(..., transport=None)` support optional injected transport for tests and future implemented adapters.
- Artifact equivalence verification covering init, transport detection, raw source preservation, ingest, query, save, status, continue, and lint.
- User guide and release readiness checklist for local Codex App / CLI MVP usage.
- `python -m llm_wiki_core` and `python -m llm_wiki_core.cli` fallback entrypoints.
- Completion criteria defining current status as MVP Local Complete.
- Roadmap separating future transport, ingest/retrieval, adapter, packaging, and organization work from MVP completion.

It does not implement actual Obsidian CLI read/write/search calls, URL ingest, batch ingest, deep semantic retrieval, advanced stale-claim lint, marketplace plugin publishing, or automatic global Codex configuration.

Example:

```powershell
python -m pip install -e .
python -m llm_wiki_core --version
llm-wiki init D:\path\to\vault --purpose "Research local LLM wiki workflows"
llm-wiki detect-transport D:\path\to\vault
llm-wiki ingest D:\path\to\vault .raw\articles\example.md
llm-wiki status D:\path\to\vault
llm-wiki continue D:\path\to\vault
llm-wiki query D:\path\to\vault "What does the wiki know about example?"
llm-wiki save D:\path\to\vault --title "Saved Insight" --content "Durable insight text."
llm-wiki lint D:\path\to\vault
.\integrations\codex\install\install.ps1 -VaultPath D:\path\to\vault -Purpose "Research local LLM wiki workflows"
.\integrations\codex\install\install.ps1 -VaultPath D:\path\to\vault -Purpose "Research local LLM wiki workflows" -DryRun
```

Run tests:

```powershell
python -m pytest
```
