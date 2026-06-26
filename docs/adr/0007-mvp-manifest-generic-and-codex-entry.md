# ADR 0007: MVP Manifest, Generic Mode, and Codex Entry Strategy

状态：已确认

## 背景

Capability mapping 后剩下三个需要确认的 MVP 取舍：

1. 是否把 `.raw/.manifest.json` 纳入 MVP。
2. 是否在 MVP 支持 LYT / PARA / Zettelkasten 等 methodology modes。
3. Codex adapter 是优先 slash command，还是先依赖自然语言触发和 skills。

## 决策

MVP 接受最小 `.raw/.manifest.json` schema，作为 MVP-lite。

MVP 只支持 generic organization mode。LYT / PARA / Zettelkasten 等 methodology modes 延后。

Codex adapter 采用双层入口策略：

- 自然语言触发必须可用。
- slash command 是目标体验，用于对齐 Claude Code 使用 `claude-obsidian` 的体验。

## 后果

- MVP 能记录来源摄取状态，降低重复 ingest 和状态漂移风险。
- MVP 的目录和页面路由保持简单，更符合先证明 LLM Wiki 闭环的目标。
- Codex App / CLI 即使 slash command 行为不完全一致，也能通过自然语言触发 + skill 完成核心工作。
- 后续仍可增加 methodology modes 和更强的命令入口体验。
