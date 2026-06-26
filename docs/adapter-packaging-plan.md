# Adapter Packaging Plan

本文件定义 MVP 阶段 Codex adapter 的包装、安装和分发策略。

当前阶段已创建 repo-local 初版安装入口；plugin marketplace 分发仍为后续目标。

## Packaging Goals

Codex adapter 应让用户在本地 Codex App 与 Codex CLI 中获得与 Claude Code 使用 `claude-obsidian` 相同的核心效果：

- 创建或继续 LLM Wiki vault。
- 摄取本地 Raw Source。
- 基于 Wiki 查询。
- 执行 lint。
- 保存长期知识。
- 维护 hot/index/log/manifest。

## Layering

```text
llm-wiki-core/
├── core contracts
├── codex adapter package
└── future claude adapter package
```

Core 不依赖 Codex。Codex adapter 依赖 core 契约。

## Codex Adapter Contents

MVP Codex adapter 包含或计划包含：

| 内容 | 说明 |
|---|---|
| `AGENTS.md` template | Codex 项目级启动说明。 |
| Skill metadata | 让 Codex 识别 wiki、ingest、query、lint、save 等触发语义。 |
| Plugin metadata | 如果采用 Codex plugin 分发，用于声明插件信息。 |
| Command mapping docs | 连接自然语言触发、目标 slash command 和 core operation。 |
| Windows install entrypoint | PowerShell 原生安装入口，当前已有初版。 |
| macOS/Linux install entrypoint | shell 安装入口，当前已有初版。 |
| Verification guide | 用户如何确认 Codex 已能触发相关能力。 |

## Install Modes

### Repo-Local Mode

用户在某个 vault 或项目内安装 adapter 文件。

优点：

- 最透明。
- 适合早期 MVP。
- 不污染全局 Codex 环境。

缺点：

- 每个 vault 需要配置。

### User-Level Skill Mode

用户将 skill 安装到 Codex 用户级 skills 目录。

优点：

- 多个 vault 可复用。
- 接近 `claude-obsidian` 的 multi-agent skill discovery 思路。

缺点：

- 需要处理 Windows/macOS 路径差异。
- 需要清楚说明如何升级。

### Plugin Mode

作为 Codex plugin 分发。

优点：

- 产品体验最好。
- 便于版本化和安装。

缺点：

- 需要更清楚的 plugin metadata 和分发流程。
- 可能依赖 Codex plugin 生态的具体规范。

## MVP Recommendation

MVP 采用两阶段包装：

1. **Repo-local first**：先保证某个 vault 内的 Codex App / CLI 能使用。
2. **User-level skill second**：再提供可复用安装路径。

Plugin mode 作为目标分发形态保留，但不阻塞 MVP。

## Windows Plan

Windows 必须原生支持。

MVP 包装应规划：

- PowerShell 安装入口。
- 不依赖 WSL。
- 不依赖 Git Bash。
- 支持路径中有空格。
- 支持 UTF-8 Markdown。

PowerShell 入口只应做薄包装，不承载 core 逻辑。

## macOS Plan

macOS 支持 shell 入口。

Shell 入口只应做薄包装，不承载 core 逻辑。

## Codex App / CLI Behavior

Codex adapter 应支持：

- 自然语言触发。
- 目标 slash command。
- 启动时读取 `AGENTS.md`。
- 按需读取 `wiki/hot.md`。
- 调用或遵循 core operation contract。

## Verification

用户应能验证：

- Codex 能识别 LLM Wiki 规则。
- Codex 能读取 hot/index。
- Codex 能执行 ingest/query/lint/save 的自然语言触发。
- 如果 slash command 可用，`/wiki` 或等效入口可触发。
- transport detection 能报告 filesystem 和 Obsidian CLI 状态。

## Relationship to Claude Adapter

Claude adapter 可保留：

- `.claude-plugin/`
- Claude Code commands。
- Claude hooks。
- Claude subagents。

这些不进入 Codex adapter，也不进入 core。

## Non-Goals

- MVP 不要求发布到任何 marketplace。
- MVP 不要求自动修改全局 Codex 配置。
- MVP 不要求支持 Codex Web / Remote。
- MVP 不要求复制 `claude-obsidian` 的 Claude plugin manifest。
- MVP 不要求生成 marketplace 级 installer 或自动全局注册逻辑。
