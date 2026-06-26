# ADR 0004: MVP Transport Policy

状态：已确认

## 背景

LLM Wiki 的核心是 raw sources / wiki / schema 三层结构。Obsidian CLI 可以提升桌面体验，但不是 LLM Wiki 运转的必要条件。

第一阶段目标是让本地 Codex App 与 CLI 能稳定维护 Markdown Wiki。

## 决策

MVP transport 分层如下：

- Filesystem transport 是必需兜底。
- Obsidian CLI transport 是可选优先。
- MCP / REST API transport 延后。

## 后果

- 没有 Obsidian CLI 的用户仍可使用 MVP。
- 有 Obsidian CLI 的桌面用户可以获得更好的 Obsidian-aware 操作。
- Transport detection 需要跨平台实现。
- MVP 不承担 MCP / REST API 的安装和配置复杂度。
