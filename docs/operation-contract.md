# Operation Contract

本文件定义 MVP core operations 的输入、输出、错误模式和验证标准。

Operations 属于 Core。Codex、Claude 或其他 Adapter 可以通过自然语言、slash command、skill 或 plugin 触发这些 operations，但不得改变其领域语义。

## Operation List

MVP operations：

- `init`
- `status`
- `continue`
- `ingest`
- `query`
- `lint`
- `save`
- `detect-transport`

## Shared Rules

所有 operation 必须遵守：

- 不修改 Raw Source。
- 使用 vault-relative paths 记录 Wiki 产物。
- 保持 `wiki/index.md`、`wiki/log.md`、`wiki/hot.md` 的语义。
- 保持 `.raw/.manifest.json` 的状态记录语义。
- 遵守 generic mode structure。
- 使用 artifact-level equivalence 作为跨 Adapter 验收标准。

## `init`

### Purpose

初始化一个 LLM Wiki vault。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | 目标 vault 根目录。 |
| `purpose` | 用户一句话描述该 vault 用途。 |
| `adapter` | 触发来源，例如 Codex App、Codex CLI、Claude Code。 |

### Output

应创建或确认存在：

- `.raw/`
- `.raw/.manifest.json`
- `wiki/`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`
- `wiki/overview.md`
- `wiki/sources/`
- `wiki/entities/`
- `wiki/concepts/`
- `wiki/questions/`
- `wiki/comparisons/`
- `wiki/meta/`
- Adapter-specific instruction file，例如 Codex `AGENTS.md`

### Error Modes

| 错误 | 处理 |
|---|---|
| vault root 不可写 | 停止并报告。 |
| 已存在非 Wiki 目录冲突 | 报告冲突，不覆盖用户文件。 |
| manifest 无法创建 | 停止 init，不继续半初始化。 |

### Validation

- required folders exist。
- required pages exist。
- manifest 是合法 JSON。
- hot/index/log/overview 有 frontmatter 或 MVP seed 内容。

## `status`

### Purpose

报告当前 vault 状态。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |

### Output

应报告：

- 是否已初始化。
- manifest source count。
- index 是否存在。
- hot cache 最近更新时间。
- log 最近条目。
- active transport。
- 建议下一步。

Milestone 11 最小实现报告：

- `initialized`。
- `missing_required_paths`。
- `source_count`。
- `preferred_transport`。
- `recent_log_entry`。
- `next_suggested_action`。

### Error Modes

| 错误 | 处理 |
|---|---|
| 不是 vault | 建议执行 init。 |
| 部分初始化 | 报告缺失项。 |

### Validation

- 不修改 Wiki。
- 不创建新文件。
- CLI 入口：`llm-wiki status <vault>`。

## `continue`

### Purpose

恢复最近上下文并建议下一步。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |

### Output

应读取：

1. `wiki/hot.md`
2. `wiki/index.md`
3. `wiki/log.md` 最近条目

应输出：

- 最近上下文摘要。
- 当前 open threads。
- 建议下一步操作。

Milestone 11 最小实现输出：

- `hot_context`。
- `index_context`。
- `recent_log_entries`。
- `files_read`。
- `next_suggested_action`。

### Error Modes

| 错误 | 处理 |
|---|---|
| hot 缺失 | 继续读取 index，并建议重建 hot。 |
| index 缺失 | 建议 lint 或 init 修复。 |

### Validation

- 默认不修改 Wiki。
- CLI 入口：`llm-wiki continue <vault>`。

## `ingest`

### Purpose

把一个本地 Raw Source 摄取进 Wiki。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |
| `source_path` | `.raw/` 下的 vault-relative path。 |
| `force` | 是否强制重新摄取。MVP 默认为 false。 |
| `transport` | 可选注入 transport；默认由 runtime selector 选择已实现 transport。 |

### Output

应更新：

- `.raw/.manifest.json`
- `wiki/sources/<source-title>.md`
- 明显相关的 `wiki/entities/*.md`
- 明显相关的 `wiki/concepts/*.md`
- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`

### Error Modes

| 错误 | 处理 |
|---|---|
| source 不在 `.raw/` 下 | 拒绝摄取。 |
| source 不存在 | 报告缺失。 |
| manifest fingerprint 未变且 `force=false` | 默认跳过或提示用户。 |
| source 无法读取 | manifest 可记录 `failed`，并报告原因。 |

### Validation

- Raw Source 未被修改。
- manifest source record 合法。
- source summary 页面存在。
- index/log/hot 已更新。
- frontmatter 合规。
- wikilinks 合规。

## `query`

### Purpose

从 Wiki 中回答问题。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |
| `question` | 用户问题。 |
| `depth` | MVP 默认 `standard`。 |

### Output

应输出：

- 基于 Wiki 的回答。
- 引用的 Wiki 页面。
- 已知 gap 或不确定性。
- 是否建议保存为 question 页面。

### Read Order

1. `wiki/hot.md`
2. `wiki/index.md`
3. 必要的相关页面

### Error Modes

| 错误 | 处理 |
|---|---|
| Wiki 未初始化 | 建议 init。 |
| index 不足以定位页面 | 明确说明 gap。 |
| 没有足够证据 | 不编造，建议添加来源。 |

### Validation

- 默认不修改 Wiki，除非用户确认保存。
- 回答应引用 Wiki 页面。

## `lint`

### Purpose

检查 Wiki 健康度。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |
| `write_report` | 是否写入 lint report。MVP 可默认为 true。 |

### Output

应检查：

- required files。
- manifest JSON。
- frontmatter。
- wikilink dead links。
- orphan pages。
- index coverage。
- hot cache length / staleness。
- log recent entries。

可写入：

```text
wiki/meta/lint-report-YYYY-MM-DD.md
```

### Error Modes

| 错误 | 处理 |
|---|---|
| manifest 不可解析 | Blocker。 |
| frontmatter 不可解析 | High。 |
| dead links | High 或 Medium，视数量与重要性。 |
| orphan pages | Medium。 |

### Validation

- lint report schema 稳定。
- 不自动修复，除非用户明确要求。

## `save`

### Purpose

把有长期价值的对话或洞见沉淀进 Wiki。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |
| `content` | 要保存的对话摘要或洞见。 |
| `title` | 可选标题。 |
| `target_type` | 可选页面类型。 |
| `transport` | 可选注入 transport；默认由 runtime selector 选择已实现 transport。 |

### Output

应创建或更新：

- `wiki/questions/*.md`，或
- `wiki/concepts/*.md`，或
- 其他合适页面。

同时更新：

- `wiki/index.md`
- `wiki/log.md`
- `wiki/hot.md`

### Error Modes

| 错误 | 处理 |
|---|---|
| 内容没有长期价值 | 建议不保存。 |
| title 冲突 | 更新已有页或请求确认。 |

### Validation

- 新页面 frontmatter 合规。
- index/log/hot 已更新。

## `detect-transport`

### Purpose

检测当前 vault 可用 transport。

### Input

| 字段 | 说明 |
|---|---|
| `vault_root` | vault 根目录。 |
| `force` | 是否强制刷新 snapshot。 |

### Output

应写入或更新 transport snapshot。

MVP runtime transport：

1. filesystem 是当前唯一 implemented runtime transport。
2. Obsidian CLI 可检测、可记录，但 actual read/write/search 未实现前不作为 preferred runtime transport。

### Error Modes

| 错误 | 处理 |
|---|---|
| Obsidian CLI 缺失 | 使用 filesystem。 |
| Obsidian CLI 调用失败 | 回退 filesystem 并报告。 |
| snapshot 无法写入 | 报告但不阻断 filesystem 使用。 |

### Validation

- filesystem 总是 available。
- preferred runtime 不得指向 unavailable 或 unimplemented transport。

## Operation Result Shape

MVP 文档层建议每个 operation 都能报告：

- operation name。
- status：`success`、`skipped`、`failed`。
- files created。
- files updated。
- warnings。
- next suggested action。

这只是输出契约，不要求当前阶段实现代码。

## 非目标

- 本文件不定义 Python 函数签名。
- 本文件不定义 CLI 参数解析实现。
- 本文件不定义 Codex 或 Claude 的具体 UI 注册方式。
