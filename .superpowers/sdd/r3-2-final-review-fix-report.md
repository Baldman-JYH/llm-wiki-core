# R3.2 Final Review Fix Report

## 变更概览

本次仅修复 final review 指定的 3 个 Important 问题，未改动 `claude-obsidian`，未引入新依赖。

### 1. 修复 URL ingest source 页摘要错误

- 修改文件：
  - `llm_wiki_core/operations/ingest.py`
  - `llm_wiki_core/operations/ingest_url.py`
  - `tests/unit/test_url_ingest_operation.py`
- 处理方式：
  - 为 `ingest_source(...)` 增加可选 `source_summary`
  - `ingest_url(...)` 在写入 wiki source 页时传入提取后的 `readable_text`
  - 保持本地文件 ingest 默认摘要行为不变
- 覆盖结果：
  - URL ingest 生成的 `wiki/sources/*.md` 的 `## Summary` 段现在包含网页正文预览，例如 `Hello Wiki` / `Useful body.`，不会再落成 `---`

### 2. 补充 manifest `content_fingerprint` lint 校验

- 修改文件：
  - `llm_wiki_core/operations/lint.py`
  - `tests/unit/test_lint_operation.py`
- 处理方式：
  - 对每个 manifest source record 增加 `content_fingerprint` 必须为非空字符串的 blocker 检查
  - 校验项名称：`manifest-content-fingerprint`
- 覆盖结果：
  - 缺失或空字符串 fingerprint 都会产生 blocker finding

### 3. 清理 R3.2 plan 文档中的本地绝对路径

- 修改文件：
  - `docs/superpowers/plans/2026-06-30-r3-2-url-ingest.md`
  - `tests/unit/test_r3_url_ingest_docs.py`
- 处理方式：
  - 将 `D:\ai\...` / `D:/ai/...` 替换为相对路径或占位描述
  - 增加文档测试，防止关键公开文档再次引入本地绝对路径

## 测试结果

### 用户指定聚焦测试

```powershell
python -m pytest tests/unit/test_url_ingest_operation.py tests/unit/test_ingest_operation.py tests/unit/test_lint_operation.py tests/unit/test_r3_url_ingest_docs.py -q
```

结果：`45 passed in 9.65s`

### 按要求补跑的 README / 文档测试

```powershell
python -m pytest tests/unit/test_r1_hardening_docs.py::test_readme_documents_machine_readable_cli_output -q
```

结果：`1 passed in 0.27s`

## 备注

- `git diff --check` 无空白错误，仅有现有的 Windows 行尾转换提示
- `pyproject.toml` 未修改，依赖仍为空
