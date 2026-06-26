# ADR 0006: Use claude-obsidian as Reference Implementation

状态：已确认

## 背景

Karpathy LLM Wiki gist 是抽象思想，描述了 raw sources、wiki、schema、ingest、query、lint、index、log 等核心模式。

`claude-obsidian` 是该思想在 Claude Code + Obsidian 场景下的具体实现案例。它已经提供可观察的用户体验、命令集合、skills、transport、hot cache、index、log 和 lint 机制。

新的 `llm-wiki-core` 目标是让 Codex App / CLI 等本地 Agent 也能获得与 Claude Code 使用 `claude-obsidian` 相同的核心效果。

## 决策

`claude-obsidian` 作为 `llm-wiki-core` 的 reference implementation。

`llm-wiki-core` 应抽象并复用 `claude-obsidian` 中跨 Agent 有价值的实践，但不复制 Claude Code 专属集成，也不直接重构 `claude-obsidian`。

## 后果

- 需要维护一份 capability mapping，说明哪些 `claude-obsidian` 能力进入 core、哪些进入 adapter、哪些延后。
- Codex adapter 的目标不是“看起来像 Claude”，而是让用户完成同一类 Wiki 维护工作并得到 artifact-level equivalent 的产物。
- 如果 Karpathy pattern 与 `claude-obsidian` 具体实现发生冲突，以 Karpathy pattern 为先；如果是实现细节差异，可优先选择更适合 Codex App / CLI 的方案。
