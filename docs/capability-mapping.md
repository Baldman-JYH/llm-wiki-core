# Capability Mapping

本文件把 `claude-obsidian` 的能力拆分到 `llm-wiki-core` 的目标结构中。

## 三层来源关系

- Karpathy LLM Wiki gist 是 abstract pattern。
- `claude-obsidian` 是 Claude Code + Obsidian 场景下的 reference implementation。
- `llm-wiki-core` 是计划中的中性 practice variant，使 Codex App / CLI 等本地 Agent 获得同等核心效果。

## 分类规则

| 分类 | 含义 |
|---|---|
| Core | 符合 Karpathy pattern，且不依赖某个 Agent 运行时的领域能力或确定性工具。 |
| Core reference | 不是独立运行能力，但其规则子集应进入 core 文档或验证规则。 |
| Adapter | 非领域能力，但需要由一个或多个运行时 adapter 提供的入口、hook 或体验层。 |
| Codex adapter | Codex App / CLI 专属入口、安装、技能、命令映射或运行时集成。 |
| Claude adapter | Claude Code 专属 plugin、commands、hooks、subagent 或 allowed-tools 集成。 |
| Deferred | 有价值但不进入第一阶段 MVP，或需要更多设计后再纳入。 |
| Excluded | 不属于中性核心或不适合新项目继承的内容。 |

## MVP 优先级

| 优先级 | 含义 |
|---|---|
| MVP | 第一阶段必须包含。 |
| MVP-lite | 第一阶段保留语义或最小版本，但不实现完整高级能力。 |
| Later | 后续版本再做。 |
| No | 不进入该项目或不进入对应层。 |

## 能力映射表

| 能力 | `claude-obsidian` 来源 | 归属 | MVP | Codex 等效方式 | 说明 |
|---|---|---|---|---|---|
| LLM Wiki 三层结构 | `WIKI.md`、`skills/wiki/SKILL.md`、`CLAUDE.md` | Core | MVP | Codex 启动时读取 core schema 与 vault 状态 | raw sources / wiki / schema 是 Karpathy pattern 核心。 |
| Raw Source 不可变规则 | `WIKI.md`、`AGENTS.md`、`skills/wiki-ingest/SKILL.md` | Core | MVP | Codex ingest 只能读取 `.raw/`，不得修改来源 | 必须保持。 |
| Wiki 目录结构 | `skills/wiki/SKILL.md`、`WIKI.md` | Core | MVP | core 定义标准 scaffold，Codex 调用 | 包括 `wiki/index.md`、`wiki/log.md`、`wiki/hot.md`、sources/entities/concepts/questions/meta。 |
| Schema / project instructions | `CLAUDE.md`、`AGENTS.md`、`WIKI.md` | Core + Adapter | MVP | core 提供 schema；Codex adapter 生成 `AGENTS.md` | Schema 是 core，具体指令文件是 adapter。 |
| Frontmatter 规则 | `skills/wiki/references/frontmatter.md`、`obsidian-markdown` | Core | MVP | core schema validation | 机器可验证字段必须稳定。 |
| Wikilink 规则 | `obsidian-markdown`、`WIKI.md` | Core | MVP | core lint 验证 wikilink 图 | 与 Obsidian 可浏览性直接相关。 |
| Hot Cache | `wiki/hot.md`、`skills/wiki/SKILL.md`、hooks | Core | MVP | Codex 启动/结束时按契约读取和更新 | Hook 是 adapter，hot cache 语义是 core。 |
| Master Index | `wiki/index.md`、`skills/wiki-query/SKILL.md` | Core | MVP | Codex query 先读 index，再读相关页面 | Karpathy pattern 明确需要。 |
| Operation Log | `wiki/log.md`、`skills/wiki/SKILL.md` | Core | MVP | Codex 每次关键操作追加 log entry | 日志格式应稳定。 |
| Overview page | `wiki/overview.md`、`WIKI.md` | Core | MVP-lite | scaffold 创建，重大变化时更新 | 可以先做轻量版本。 |
| Source summary pages | `skills/wiki-ingest/SKILL.md` | Core | MVP | ingest 创建 `wiki/sources/` 页面 | MVP 应支持单来源。 |
| Entity pages | `skills/wiki-ingest/SKILL.md` | Core | MVP-lite | ingest 可创建明显实体页 | 第一阶段可以保守生成。 |
| Concept pages | `skills/wiki-ingest/SKILL.md` | Core | MVP-lite | ingest 可创建明显概念页 | 第一阶段可以保守生成。 |
| Question pages | `skills/wiki-query/SKILL.md` | Core | MVP-lite | query 后可建议保存为 question 页面 | 不强制每次保存。 |
| Comparison pages | `WIKI.md`、wiki seed content | Core | Later | 后续作为 query/save 产物 | MVP 不必优先。 |
| Scaffold workflow | `commands/wiki.md`、`skills/wiki/SKILL.md` | Core + Adapter | MVP | core 定义步骤；Codex adapter 提供 `/wiki` 或等效入口 | 核心是创建结构，命令入口属于 adapter。 |
| Single-source ingest | `skills/wiki-ingest/SKILL.md` | Core | MVP | Codex 命令触发 core ingest workflow | 第一阶段关键闭环。 |
| Batch ingest | `skills/wiki-ingest/SKILL.md`、`agents/wiki-ingest.md` | Core + Adapter | Later | 后续支持批处理和子任务协调 | MVP 先单来源。 |
| URL ingest | `skills/wiki-ingest/SKILL.md`、`defuddle` | Deferred | Later | 以后通过 web cleaner 或 fetch adapter | 涉及网络、安全和清洗。 |
| Image / vision ingest | `skills/wiki-ingest/SKILL.md` | Deferred | Later | 以后按 Agent 能力适配 | 非 MVP。 |
| Query quick / standard / deep | `skills/wiki-query/SKILL.md` | Core | MVP-lite | MVP 先支持 standard；保留 mode 术语 | quick/deep 可后续扩展。 |
| Filing query answers back | `skills/wiki-query/SKILL.md` | Core | MVP-lite | Codex 提示用户是否保存 | 符合 Karpathy pattern。 |
| Gap handling | `skills/wiki-query/SKILL.md` | Core | MVP | 回答不足时标记 gap 或建议来源 | 轻量可做。 |
| Wiki lint | `skills/wiki-lint/SKILL.md` | Core | MVP | core lint contract + Codex 命令入口 | MVP 检查 frontmatter、死链、孤页、index/log/hot。 |
| Lint report | `skills/wiki-lint/SKILL.md` | Core | MVP-lite | 生成 `wiki/meta/lint-report-YYYY-MM-DD.md` | 初版可先稳定 schema。 |
| Save conversation | `skills/save/SKILL.md`、`commands/save.md` | Core + Adapter | MVP-lite | Codex adapter 提供 save 入口，core 定义保存规则 | 保存长期知识，不保存噪声。 |
| Transport contract | `skills/wiki-cli/SKILL.md`、`wiki/references/transport-fallback.md` | Core | MVP | Python transport detection：filesystem runtime + Obsidian CLI boundary | 语义进 core，具体入口跨平台实现。 |
| Filesystem transport | `wiki-cli` fallback、直接文件读写 | Core | MVP | Codex 本地文件读写 | 必需兜底。 |
| Obsidian CLI transport | `skills/wiki-cli/SKILL.md`、`scripts/detect-transport.sh` | Core boundary | Later | MVP 只检测 availability 并记录 `implemented: false` | Actual read/write/search 实现前不作为 runtime preferred。 |
| MCP transport | `WIKI.md`、`mcp-setup.md` | Deferred | Later | 后续 transport adapter | 第一阶段不纳入。 |
| REST API transport | `WIKI.md`、`rest-api.md` | Deferred | Later | 后续 transport adapter | 第一阶段不纳入。 |
| `.raw/.manifest.json` delta tracking | `skills/wiki-ingest/SKILL.md`、`AGENTS.md` | Core | MVP-lite | core manifest schema | 建议进入 MVP-lite，避免重复 ingest。 |
| Per-file locking | `scripts/wiki-lock.sh`、`skills/wiki-ingest` | Core | Later | 后续 Python lock 实现 | MVP 单用户单操作可先不做完整并发。 |
| Auto-commit hook | `hooks/hooks.json` | Claude adapter | No | Codex 不默认自动 commit | 这是 Claude hook 行为，不是 core 必需。 |
| SessionStart hot cache hook | `hooks/hooks.json` | Adapter | MVP-lite | Codex adapter 启动说明/skill 触发读取 hot | hot 语义进 core，hook 实现进 adapter。 |
| Stop hook hot-cache reminder | `hooks/hooks.json` | Adapter | Later | Codex adapter 可提供结束检查 | MVP 可手动/命令化。 |
| Claude plugin manifest | `.claude-plugin/plugin.json` | Claude adapter | No | 不进入 Codex core | 仅 Claude 分发。 |
| Claude slash commands | `commands/*.md` | Claude adapter + Mapping source | No | Codex adapter 定义等效命令 | 不能照搬实现细节。 |
| Codex `AGENTS.md` bootstrap | `AGENTS.md` | Codex adapter | MVP | 生成 Codex 专用 AGENTS 模板 | `claude-obsidian` 已证明可跨 Agent。 |
| Codex skills/plugin metadata | `AGENTS.md`、`setup-multi-agent.sh` | Codex adapter | MVP | `.agents/skills` 或 Codex plugin 方案 | 需要后续按 Codex 官方机制细化。 |
| PowerShell installer | 无直接等价；`setup-multi-agent.sh` 是 bash | Codex adapter | MVP | `install.ps1` 设计 | Windows 原生优先。 |
| macOS/Linux installer | `setup-multi-agent.sh`、`setup-vault.sh` | Codex adapter | MVP-lite | shell wrapper 调用 core | 但核心逻辑不写在 shell。 |
| Methodology modes | `skills/wiki-mode`、`scripts/wiki-mode.py` | Deferred | Later | 后续作为可选 organization module | 当前 MVP 先 generic。 |
| LYT / PARA / Zettelkasten templates | `skills/wiki-mode/templates/*` | Deferred | Later | 后续模板包 | 非第一阶段闭环。 |
| Hybrid retrieval | `skills/wiki-retrieve`、`scripts/retrieve.py` | Deferred | Later | 后续 retrieval module | 复杂度高，且 Karpathy pattern 小规模可先靠 index。 |
| BM25 index | `scripts/bm25-index.py` | Deferred | Later | 后续 local search | 可作为第二阶段增强。 |
| Contextual prefix | `scripts/contextual-prefix.py` | Deferred | Later | 需 egress consent | 不进 MVP。 |
| Ollama rerank | `scripts/rerank.py` | Deferred | Later | 本地可选增强 | 不进 MVP。 |
| DragonScale log fold | `skills/wiki-fold` | Deferred | Later | 后续 memory extension | 高级记忆机制。 |
| Deterministic page address | `allocate-address.sh`、ingest/lint sections | Deferred | Later | 后续 Python address allocator | MVP 不必。 |
| Semantic tiling lint | `tiling-check.py`、`wiki-lint` | Deferred | Later | 后续 advanced lint | 需额外校准。 |
| Boundary-first autoresearch | `autoresearch`、`boundary-score.py` | Deferred | Later | 后续 research module | 非 MVP。 |
| Autoresearch | `skills/autoresearch`、`commands/autoresearch.md` | Deferred | Later | 后续可选技能 | 涉及网络与 source policy。 |
| Defuddle web cleaner | `skills/defuddle` | Deferred | Later | 后续 URL ingest helper | 非 MVP。 |
| Canvas visual layer | `skills/canvas`、`commands/canvas.md` | Deferred | Later | 后续 Obsidian visual adapter | 非 Karpathy core 必需。 |
| Obsidian Bases dashboard | `skills/obsidian-bases`、README | Deferred | Later | 后续 Obsidian enhancement | 非 MVP。 |
| Obsidian Markdown reference | `skills/obsidian-markdown` | Core reference | MVP-lite | core docs 引用必要语法 | 只吸收 wikilink/frontmatter/callout 必需子集。 |
| CSS snippets / visual customization | `skills/wiki/references/css-snippets.md` | Deferred | Later | 后续 Obsidian theme helper | 不影响 Wiki core。 |
| Git setup / Obsidian Git | `skills/wiki/references/git-setup.md` | Deferred | Later | 后续 optional docs | 不作为 MVP 必需。 |
| Pre-commit verifier agent | `agents/verifier.md` | Claude adapter / Dev workflow | Later | 可作为开发流程参考 | 不进入用户 core。 |
| Wiki ingest subagent | `agents/wiki-ingest.md` | Claude adapter | Later | Codex 多代理能力另行设计 | MVP 不依赖 subagent。 |
| Wiki lint subagent | `agents/wiki-lint.md` | Claude adapter | Later | Codex 多代理能力另行设计 | MVP 不依赖 subagent。 |
| Community footer / marketing output | `skills/wiki/SKILL.md` | Excluded | No | 不继承 | 与中性 core 无关。 |
| Release blog workflow | `CLAUDE.md` | Excluded | No | 不继承 | 项目发布营销流程，不是 LLM Wiki core。 |

## Core MVP 能力集合

第一阶段 core 应至少包括：

1. Vault scaffold。
2. Raw Source 只读约束。
3. Wiki 标准目录。
4. Schema / frontmatter / wikilink 规则。
5. `index.md`、`log.md`、`hot.md`。
6. 单来源 ingest。
7. 基础 query。
8. 基础 lint。
9. save 语义的最小版本。
10. filesystem transport。
11. Obsidian CLI detection / unimplemented boundary。
12. artifact-level equivalence 验证契约。

## Codex Adapter MVP 能力集合

第一阶段 Codex adapter 应至少包括：

1. Codex App / CLI 启动说明。
2. `AGENTS.md` 模板。
3. Codex skill 或 plugin 分发策略。
4. `/wiki` 或等效命令映射。
5. `ingest`、`query`、`lint`、`save` 命令语义映射。
6. Windows PowerShell 安装入口。
7. macOS shell 安装入口。
8. 与 core transport detection 的调用约定。

## Claude Adapter 能力集合

Claude adapter 可以保留或后续重建：

1. `.claude-plugin/` manifest。
2. Claude Code commands。
3. Claude hooks。
4. Claude subagent 工作流。
5. Claude-specific allowed-tools 兼容字段。

这些不应污染 core。

## Deferred 能力集合

以下能力有价值，但不进入第一阶段 MVP：

1. URL ingest。
2. defuddle。
3. autoresearch。
4. canvas。
5. hybrid retrieval。
6. DragonScale。
7. methodology modes 完整迁移。
8. semantic tiling。
9. boundary-first research。
10. Obsidian Bases dashboard。
11. advanced multi-writer locking。

## 已确认的 MVP 取舍

- MVP 接受最小 `.raw/.manifest.json` schema，作为 MVP-lite。理由是它可以显著降低重复 ingest 和状态漂移风险。
- MVP 只支持 generic organization mode。LYT / PARA / Zettelkasten 等 methodology modes 完整迁移延后。
- Codex adapter 入口采用双层策略：自然语言触发必须可用，slash command 作为目标体验对齐。

## 已建立的细化契约

- `docs/manifest-schema.md` 定义最小 manifest schema 的字段、状态语义、路径规则和验证规则。
- `docs/generic-mode-structure.md` 定义 generic mode 的默认目录、页面类型路由、frontmatter、index/log/hot 格式。
- `docs/codex-command-contract.md` 定义 Codex App / CLI 中自然语言触发与 slash command 的双层命令语义。
- `docs/operation-contract.md` 定义 MVP core operations 的输入、输出、错误模式和验证标准。
- `docs/test-fixture-plan.md` 定义 MVP parity tests 的 fixture vault 计划和 artifact-level assertions。
- `docs/adapter-packaging-plan.md` 定义 Codex adapter 的 repo-local、user-level skill、plugin 三种包装路径。
- `docs/implementation-readiness-checklist.md` 定义进入实现阶段前必须满足的检查项。
- `docs/project-skeleton-plan.md` 定义未来代码目录计划，但不授权立即创建代码。
- `docs/milestone-plan.md` 定义从 planning complete 到 Codex adapter MVP 的阶段路线。

## 后续可继续细化

- 用户审阅并确认是否进入项目骨架和 MVP 实现阶段。
- 进入实现前，按 `docs/implementation-readiness-checklist.md` 执行检查。
