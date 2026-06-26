# Manifest Schema

本文件定义 MVP 阶段的最小 `.raw/.manifest.json` 契约。

Manifest 用来记录 Raw Source 与 Wiki 产物之间的关系，避免重复 ingest 和状态漂移。它是状态记录，不是 Raw Source 内容的替代品。

## 位置

Manifest 固定放在 vault 的 Raw Source 层：

```text
.raw/.manifest.json
```

## 设计原则

- Manifest 属于 Core。
- Manifest 必须可由不同 Agent adapter 读写。
- Manifest 必须保持 JSON，避免依赖某个 Agent 的专有格式。
- Manifest 不保存 Raw Source 全文。
- Manifest 不替代 `wiki/log.md`。Manifest 记录状态，Log 记录时间线。
- Manifest 不替代 `wiki/index.md`。Manifest 帮助机器判断摄取状态，Index 帮助人和 Agent 导航内容。

## MVP Schema

MVP 使用一个稳定、保守的顶层结构：

```json
{
  "schema_version": 1,
  "updated": "2026-06-25T00:00:00+08:00",
  "sources": {
    "articles/example.md": {
      "source_path": ".raw/articles/example.md",
      "source_type": "file",
      "status": "ingested",
      "first_ingested": "2026-06-25T00:00:00+08:00",
      "last_ingested": "2026-06-25T00:00:00+08:00",
      "content_fingerprint": "sha256:...",
      "generated_pages": [
        "wiki/sources/Example.md",
        "wiki/concepts/Example Concept.md"
      ],
      "updated_pages": [
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md"
      ],
      "notes": ""
    }
  }
}
```

## Required Fields

顶层：

| 字段 | 类型 | 说明 |
|---|---|---|
| `schema_version` | number | Manifest schema 版本。MVP 固定为 `1`。 |
| `updated` | string | Manifest 最近更新时间，ISO 8601。 |
| `sources` | object | 以 vault-relative raw source key 索引的来源记录。 |

来源记录：

| 字段 | 类型 | 说明 |
|---|---|---|
| `source_path` | string | Raw Source 的 vault-relative path，必须位于 `.raw/` 下。 |
| `source_type` | string | MVP 只要求 `file`。 |
| `status` | string | `ingested`、`skipped`、`failed` 之一。 |
| `first_ingested` | string | 首次摄取时间，ISO 8601。 |
| `last_ingested` | string | 最近摄取时间，ISO 8601。 |
| `content_fingerprint` | string | 内容指纹。推荐 `sha256:<hex>`。 |
| `generated_pages` | array | 本来源首次生成的 Wiki 页面。 |
| `updated_pages` | array | 本次摄取更新的 Wiki 页面。 |
| `notes` | string | 可选说明。没有说明时为空字符串。 |

## Source Key

`sources` 的 key 使用去掉 `.raw/` 前缀后的路径：

```text
.raw/articles/example.md -> articles/example.md
```

理由：

- key 稳定且短。
- 仍可从 `source_path` 还原完整 vault-relative path。
- 便于未来支持 raw source 子目录。

## Status Semantics

| status | 含义 |
|---|---|
| `ingested` | 来源已成功摄取，相关 Wiki 页面已更新。 |
| `skipped` | 本次跳过，通常因为内容指纹未变或用户明确跳过。 |
| `failed` | 摄取失败，应在 `notes` 中记录简短原因。 |

## Fingerprint

MVP 推荐使用 Raw Source 文件内容的 SHA-256：

```text
sha256:<hex>
```

Fingerprint 用来判断来源是否发生变化。即使 fingerprint 未变，用户仍可要求强制重新摄取。

## Page Paths

`generated_pages` 与 `updated_pages` 必须使用 vault-relative path：

```text
wiki/sources/Example.md
wiki/concepts/Example Concept.md
```

不要使用绝对路径。这样 manifest 可以随 vault 移动。

## Ingest Behavior

Agent 执行 ingest 时：

1. 读取 Raw Source。
2. 计算或记录 content fingerprint。
3. 查找 manifest 中是否已有记录。
4. 如果 fingerprint 未变，默认提示或跳过，不重复摄取。
5. 如果用户要求强制摄取，应更新 `last_ingested` 和相关页面列表。
6. 摄取完成后更新 manifest、index、log、hot。

## Validation Rules

MVP lint 应检查：

- Manifest 是合法 JSON。
- `schema_version` 存在且为 `1`。
- 每个 `source_path` 都位于 `.raw/` 下。
- 每个 `generated_pages` / `updated_pages` 路径都位于 `wiki/`、`.raw/.manifest.json` 或允许的 meta 文件范围内。
- `status` 值合法。
- `content_fingerprint` 非空。

## 非目标

- MVP 不记录完整 source text。
- MVP 不记录复杂 provenance graph。
- MVP 不要求支持 remote URL source。
- MVP 不要求支持 image / vision source。
- MVP 不定义并发 merge 规则。
