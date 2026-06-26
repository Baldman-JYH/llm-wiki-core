# Transport Contract

Transport 是 Agent 读写 Wiki 文件的通道。

## MVP Transport 顺序

第一阶段 MVP 使用以下顺序：

1. Filesystem transport，当前唯一已实现 runtime transport。
2. Obsidian CLI transport，可检测、可记录，但在 actual read/write/search 实现前不作为 preferred runtime transport。

MCP 与 REST API transport 延后。

## Filesystem Transport

Filesystem transport 是最低可用通道。

Milestone 9 起，filesystem transport 提供最小可执行 API：

| 方法 | 说明 |
|---|---|
| `read_text(relative_path)` | 读取 UTF-8 文本。 |
| `write_text(relative_path, content)` | 创建或覆盖 UTF-8 文本文件，并创建必要父目录。 |
| `append_text(relative_path, content)` | 向 UTF-8 文本文件末尾追加内容，并创建必要父目录。 |
| `exists(relative_path)` | 判断 vault-relative path 是否存在。 |
| `list_markdown(root="wiki")` | 按稳定顺序列出 Markdown 文件。 |
| `search_text(query, root="wiki")` | 对 Markdown 文件执行确定性的大小写不敏感子串搜索。 |

它不依赖 Obsidian、MCP、REST API、WSL 或 Git Bash。

所有公开方法都接受 vault-relative path，并拒绝绝对路径、`..` traversal 或任何解析到 vault 外部的路径。

`search_text` 是 transport 级本地文本搜索，不是 hybrid retrieval、BM25、向量搜索或 LLM 综合。

Milestone 10 起，`query` 和 `lint` 默认通过 filesystem transport 访问 Wiki 文件。CLI 行为不变；后续 adapter 可以在不改变 operation 语义的前提下注入其他 transport。

## Obsidian CLI Transport

Obsidian CLI transport 是桌面体验增强通道。

当本机存在 Obsidian CLI 时，系统可以记录它的可用性，为未来增强保留边界。只有当 actual transport 实现完成并通过测试后，系统才可以优先使用它进行：

- read。
- write。
- append。
- search。
- backlinks。
- daily note。

当 Obsidian CLI 缺失或失败时，必须回退 filesystem transport。

Milestone 16 起，transport snapshot 将 detection 与 implementation 分开：

- `available: true` 表示本机检测到了 Obsidian CLI 可执行文件。
- `implemented: false` 表示 core 尚未实现 actual Obsidian CLI read/write/search。
- `preferred: filesystem` 表示当前 operation 安全使用 filesystem transport。

`ObsidianCliTransport` 当前是 contract placeholder；调用其 `read_text`、`write_text`、`append_text`、`exists`、`list_markdown` 或 `search_text` 会抛出明确的未实现错误。

## Transport Snapshot

系统应维护 transport snapshot，用来记录当前机器可用 transport。

建议字段：

- schema version。
- detected at。
- platform。
- vault root。
- preferred。
- fallback chain。
- available transports。
- per-transport implemented state。
- per-transport reason。
- manual override。

## Runtime Transport Selection

Transport detection 是机器状态记录，runtime selection 是 operation 实际使用通道的选择。

Milestone 17 起，默认 runtime selection 遵循以下规则：

- snapshot 只作为 advisory metadata。
- 只有 `available: true` 且 `implemented: true` 的 transport 才能成为 runtime transport。
- 当前 MVP 唯一 implemented runtime transport 是 filesystem。
- 如果旧 snapshot 或未来 snapshot 将 `preferred` 指向未实现 transport，operation 必须回落 filesystem。
- `status` 和 `continue` 会保留 fallback warning，帮助用户理解为什么没有使用 snapshot 中的 preferred transport。

当前使用 runtime selector 的 operations：

- `query`
- `lint`
- `status`
- `continue`
- `ingest`
- `save`

`init` 仍直接创建 vault scaffold；在 actual Obsidian CLI write transport 实现前不迁移到其他 write path。

## 跨平台要求

- 核心检测逻辑应使用 Python。
- Windows 入口使用 PowerShell。
- macOS / Linux 入口使用 shell。
- 路径处理必须支持 Windows 路径、空格和非 ASCII 字符。

## 非目标

- MVP 不要求自动配置 MCP。
- MVP 不要求安装 Obsidian。
- MVP 不要求 Obsidian CLI 必然存在。
- Milestone 9 不要求实现 Obsidian backlinks、daily note 或 Obsidian CLI 实调用。
