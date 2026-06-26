# Codex Command Contract

本文件定义 Codex App / CLI adapter 的命令语义。

MVP 采用双层入口策略：

1. 自然语言触发必须可用。
2. Slash command 是目标体验，用于对齐 Claude Code 使用 `claude-obsidian` 的体验。

如果 Codex App 与 Codex CLI 对 slash command 的支持存在差异，应优先保证自然语言触发 + skill 能完成同等核心工作。

## 设计原则

- 命令语义对齐 `claude-obsidian` 的核心体验。
- 入口属于 Codex adapter，不属于 core。
- Core 只定义操作契约，不关心用户如何触发。
- 自然语言入口不能是二等路径；它必须完整可用。
- Slash command 可作为更顺手的 UX 层。

## Command Mapping

| 用户意图 | 自然语言触发示例 | 目标 slash command | Core operation |
|---|---|---|---|
| 初始化或继续 Wiki | `set up wiki`、`scaffold vault`、`continue wiki` | `/wiki` | `init` / `status` / `continue` |
| 摄取本地来源 | `ingest .raw/articles/a.md`、`process this source` | `/wiki ingest <source>` | `ingest` |
| 查询 Wiki | `what do you know about X`、`query: X` | `/wiki query <question>` | `query` |
| 健康检查 | `lint the wiki`、`health check` | `/wiki lint` | `lint` |
| 保存对话 | `save this conversation`、`file this insight` | `/wiki save [title]` | `save` |
| 检测 transport | `check wiki transport` | `/wiki transport` | `detect-transport` |

## `/wiki` Semantics

`/wiki` 是目标体验入口。

当 vault 未初始化时：

1. 检查当前目录是否已有 `.raw/` 和 `wiki/`。
2. 如未初始化，询问一个问题：这个 vault 用来做什么？
3. 使用 generic mode scaffold 基础结构。
4. 创建或更新项目指令文件。
5. 创建 `index.md`、`log.md`、`hot.md`、`overview.md`。
6. 创建 `.raw/.manifest.json`。
7. 检测 transport。
8. 给出下一步建议：放入 Raw Source 后执行 ingest。

当 vault 已初始化时：

1. 读取 `wiki/hot.md`。
2. 读取 `wiki/index.md`。
3. 检查最近 log。
4. 报告当前状态。
5. 建议继续 ingest、query、lint 或 save。

## `ingest` Semantics

自然语言：

```text
ingest .raw/articles/example.md
process this source
add this to the wiki
```

目标 slash command：

```text
/wiki ingest .raw/articles/example.md
```

行为：

1. 确认目标位于 `.raw/`。
2. 读取 Raw Source，但不修改它。
3. 检查 `.raw/.manifest.json`。
4. 如果来源已摄取且 fingerprint 未变，提示是否跳过或强制重新摄取。
5. 创建或更新 source summary。
6. 保守创建或更新明显 entity / concept 页面。
7. 更新 `wiki/index.md`。
8. 更新 `wiki/log.md`。
9. 更新 `wiki/hot.md`。
10. 更新 manifest。

## `query` Semantics

自然语言：

```text
what do you know about X?
query: X
based on the wiki, explain X
```

目标 slash command：

```text
/wiki query X
```

行为：

1. 读取 `wiki/hot.md`。
2. 读取 `wiki/index.md`。
3. 选择必要的相关页面。
4. 综合回答，并引用 Wiki 页面。
5. 如果问题暴露知识缺口，明确说明 gap。
6. 如果回答有长期价值，建议保存到 `wiki/questions/`。

## `lint` Semantics

自然语言：

```text
lint the wiki
health check
find wiki gaps
```

目标 slash command：

```text
/wiki lint
```

行为：

1. 检查 frontmatter。
2. 检查 wikilink 死链。
3. 检查孤页。
4. 检查 index 是否包含主要页面。
5. 检查 log 是否有最近操作。
6. 检查 hot cache 是否过期或过长。
7. 检查 manifest 是否可解析。
8. 输出或写入 lint report。

## `save` Semantics

自然语言：

```text
save this conversation
file this insight
save as "Topic"
```

目标 slash command：

```text
/wiki save [title]
```

行为：

1. 判断聊天内容是否有长期知识价值。
2. 选择保存为 question、concept、source note 或 session note。
3. 创建或更新对应 Wiki 页面。
4. 更新 `wiki/index.md`。
5. 更新 `wiki/log.md`。
6. 更新 `wiki/hot.md`。

## `detect-transport` Semantics

自然语言：

```text
check wiki transport
which transport is active?
```

目标 slash command：

```text
/wiki transport
```

行为：

1. 检测 filesystem transport。
2. 检测 Obsidian CLI transport。
3. 写入 transport snapshot。
4. 设置 preferred transport：Obsidian CLI 优先，filesystem 兜底。
5. 报告当前可用 transport。

## Codex App / CLI 差异

MVP 不假设 Codex App 和 Codex CLI 的 slash command 能力完全一致。

因此每个目标 slash command 必须有自然语言等效触发。

## Adapter Responsibilities

Codex adapter 负责：

- 提供 `AGENTS.md` 模板。
- 暴露技能或 plugin metadata。
- 映射自然语言触发和 slash command。
- 指导用户在 Codex App / CLI 中使用。
- 调用 core operation。

Core 不负责：

- Codex UI 行为。
- Codex App 与 CLI 的具体命令注册细节。
- Claude Code command 兼容层。

## 非目标

- MVP 不实现 URL ingest 命令。
- MVP 不实现 `/autoresearch`。
- MVP 不实现 `/canvas`。
- MVP 不实现 hybrid retrieval 命令。
- MVP 不要求 slash command 是唯一入口。
