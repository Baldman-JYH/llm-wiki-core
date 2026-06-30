# 项目进展文档

## 阶段 1：R3.2 final review fix 启动与现状确认

状态：进行中

### 本阶段目标

在 `llm-wiki-core` 仓库内仅修复 final review 提出的 3 个 Important 问题，不改动外部 `claude-obsidian` 仓库，不回滚已有工作。

### 已确认信息

- 当前工作目录限定为 `D:/ai/llmWiki/llm-wiki-core`
- 目标问题共 3 个：
  1. URL ingest 生成 source 页摘要错误地取到了 frontmatter / metadata
  2. lint 未校验 manifest source record 的 `content_fingerprint`
  3. R3.2 计划文档含本地绝对路径
- 相关实现文件已定位：
  - `llm_wiki_core/operations/ingest.py`
  - `llm_wiki_core/operations/ingest_url.py`
  - `llm_wiki_core/operations/lint.py`
  - `tests/unit/test_url_ingest_operation.py`
  - `tests/unit/test_lint_operation.py`
  - `tests/unit/test_r3_url_ingest_docs.py`
  - `docs/superpowers/plans/2026-06-30-r3-2-url-ingest.md`

### 当前判断

- URL source 页摘要问题的根因与 review 描述一致：`ingest_source()` 目前从 raw source 文本首个非空行生成 summary，而 URL raw source 以 frontmatter 开头。
- 最小修复路径应是给 `ingest_source(...)` 增加可选摘要输入，并仅在 URL ingest 调用时传入提取后的正文预览，保持本地文件 ingest 行为不变。
- lint 的 manifest record 校验目前只检查了 `source_type` 与 `source_path`，尚未覆盖 `content_fingerprint` 非空约束。
- 文档测试当前只覆盖内容契约，尚未防止 R3.2 文档重新引入 `D:\\ai` / `D:/ai` 形式的本地绝对路径。

### 下一步

先补三类失败测试，再进入最小实现修复。

## 阶段 2：失败测试确认与最小修复落地

状态：进行中

### 已完成

- 已补充并跑出 3 处失败测试：
  - `tests/unit/test_url_ingest_operation.py` 新增断言，证明 URL source 页 `## Summary` 仍错误取到了 frontmatter 起始内容
  - `tests/unit/test_lint_operation.py` 新增负例，证明缺失或空的 `content_fingerprint` 当前不会触发 blocker
  - `tests/unit/test_r3_url_ingest_docs.py` 新增文档防护，证明 R3.2 plan 仍包含 `D:\ai` 形式的绝对路径
- 已开始最小实现修复：
  - 在 `ingest_source(...)` 中加入可选 `source_summary`
  - 在 `ingest_url(...)` 调用 `ingest_source(...)` 时传入提取后的 `readable_text`
  - 在 `lint.py` 中加入 `manifest-content-fingerprint` blocker 校验
  - 在 `docs/superpowers/plans/2026-06-30-r3-2-url-ingest.md` 中将本地绝对路径替换为相对或占位表述

### 当前目标

重新运行聚焦测试，确认三类问题都从红转绿；随后写修复报告并提交中文 commit。

## 阶段 3：验证完成与交付整理

状态：已完成

### 验证结果

- 已通过用户指定聚焦测试：
  - `python -m pytest tests/unit/test_url_ingest_operation.py tests/unit/test_ingest_operation.py tests/unit/test_lint_operation.py tests/unit/test_r3_url_ingest_docs.py -q`
  - 结果：`45 passed`
- 已通过 README 相关补充回归测试：
  - `python -m pytest tests/unit/test_r1_hardening_docs.py::test_readme_documents_machine_readable_cli_output -q`
  - 结果：`1 passed`

### 已完成交付物

- URL ingest source 页摘要改为优先使用调用方提供的正文摘要预览，修复 `---` / frontmatter 被写入 `## Summary` 的问题
- lint 补充 `content_fingerprint` 非空字符串 blocker 校验
- R3.2 plan 文档中的本地绝对路径已替换为相对或占位表述
- 已生成最终修复报告：
  - `.superpowers/sdd/r3-2-final-review-fix-report.md`

### 下一步

执行中文 commit，并向用户回报提交信息、测试结果、关注点和报告路径。
