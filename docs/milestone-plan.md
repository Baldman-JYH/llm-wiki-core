# Milestone Plan

本文件定义 MVP 从规划到实现的阶段计划。

规划阶段已结束；当前按里程碑推进 MVP 实现与复核。

## Milestone 0: Planning Complete

目标：确认实现前规划闭合。

产物：

- capability mapping。
- manifest schema。
- generic mode structure。
- Codex command contract。
- operation contract。
- test fixture plan。
- adapter packaging plan。
- implementation readiness checklist。
- project skeleton plan。

退出条件：

- 用户确认可以进入项目骨架和 MVP 实现阶段。

## Milestone 1: Project Skeleton

目标：建立项目骨架，不实现完整业务逻辑。

产物：

- Python package skeleton。
- docs 保持当前结构。
- tests fixture directories。
- integrations/codex placeholder。
- project metadata。

验收：

- 没有复制 `claude-obsidian` 代码。
- 没有破坏现有规划文档。
- 文件结构符合 `project-skeleton-plan.md`。

## Milestone 2: Scaffold + Generic Mode

目标：实现 `init` 最小闭环。

产物：

- 创建 `.raw/`。
- 创建 `.raw/.manifest.json`。
- 创建 `wiki/` 结构。
- 创建 index/log/hot/overview seed 页面。
- 创建 Codex `AGENTS.md` 模板输出。

验收：

- F0 empty fixture 可通过。
- Windows 路径可用。
- 不依赖 Obsidian CLI。

## Milestone 3: Transport Detection

目标：实现 filesystem runtime + Obsidian CLI boundary detection。

产物：

- filesystem transport。
- Obsidian CLI detection metadata。
- transport snapshot。
- fallback chain。

验收：

- 没有 Obsidian CLI 时 filesystem 可用。
- 有 Obsidian CLI 时记录 available；actual read/write/search 实现前 preferred runtime 仍为 filesystem。
- snapshot 合法。

## Milestone 4: Manifest + Ingest

目标：实现单来源 ingest MVP。

产物：

- content fingerprint。
- manifest source record。
- source summary page。
- 保守 entity/concept page creation。
- index/log/hot 更新。

验收：

- F2 single source fixture 可通过。
- Raw Source 未被修改。
- 重复 ingest 可识别。

## Milestone 5: Query + Save

目标：实现基础 query 和 save。

产物：

- hot -> index -> pages read order。
- cited Wiki answer。
- gap reporting。
- save to question/concept page。
- index/log/hot 更新。

验收：

- F3 existing knowledge fixture 可通过。
- query 默认不修改 Wiki。
- save 修改内容可验证。

## Milestone 6: Lint + Parity Validation

目标：实现基础 lint 和 artifact-level validation。

产物：

- frontmatter check。
- dead wikilink check。
- orphan page check。
- manifest check。
- index/log/hot check。
- lint report。

验收：

- F4 broken wiki fixture 可报告 expected findings。
- lint 不自动修复。

## Milestone 7: Codex Adapter MVP

目标：让 Codex App / CLI 具备可用体验。

产物：

- Codex `AGENTS.md` template。
- Codex skill/plugin metadata draft。
- natural language triggers。
- target slash command mapping。
- PowerShell install plan 或初版入口。
- macOS shell install plan 或初版入口。

验收：

- 用户能在 Codex 本地环境中按自然语言触发核心流程。
- slash command 作为目标体验有清晰说明。

## Milestone 8: MVP Review

目标：确认 MVP 是否达到 `claude-obsidian` 核心体验等效。

检查：

- 是否符合 Karpathy gist。
- 是否保留 `claude-obsidian` 关键实践效果。
- 是否没有把 Claude 专属机制放进 core。
- 是否 Windows 原生可用。
- 是否 Codex App / CLI 可用。

## Deferred Milestones

后续版本：

- Methodology modes。
- URL ingest / defuddle。
- Autoresearch。
- Canvas。
- Hybrid retrieval。
- DragonScale。
- Advanced locking。
- MCP / REST API transport。
- Actual Obsidian CLI read/write/search。

## Non-Goals

- MVP 不追求完整复刻 `claude-obsidian` 所有高级能力。
- MVP 不追求所有 LLM-authored content 字节级一致。
- MVP 不优先支持 Codex Web / Remote。
