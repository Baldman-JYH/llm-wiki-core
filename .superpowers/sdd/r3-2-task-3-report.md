# R3.2 Task 3 Report

## 范围

- 继续完成 `llm_wiki_core/operations/ingest_url.py` 的 URL ingest operation
- 复核并整理已有 Task 3 半成品
- 仅修改 Task 3 必要代码与测试
- 清理误放的仓库内 `codex_doc`

## 实际变更

### 1. URL ingest operation 收口

- 保留并复核 `UrlIngestResult`
- 保留 `ingest_url(...)` 的主流程：
  - 校验 `http/https` URL
  - 通过 `fetcher` 或默认 `_fetch_url(...)` 抓取内容
  - 解码响应文本并提取可读文本
  - 写入 immutable snapshot bundle：
    - `response.html` / `response.txt`
    - `metadata.json`
    - `source.md`
  - 调用 `ingest_source(...)` 更新 wiki 页面与 manifest provenance

### 2. 修正计划常量

根据 `r3-2-task-2-brief.md` 中已明确的计划值，修正为：

- `DEFAULT_TIMEOUT_SECONDS = 10`
- `MAX_RESPONSE_BYTES = 2_000_000`

此前半成品中的值分别为 `30` 和 `5 * 1024 * 1024`，与计划不一致。

### 3. 测试补强

在 `tests/unit/test_url_ingest_operation.py` 新增：

- `test_url_fetch_defaults_match_brief_plan_values`

该测试先验证计划常量，初次运行时确实失败，随后在修正实现后转绿。

### 4. 工作区清理

- 删除误放目录：`D:/ai/llmWiki/llm-wiki-core/codex_doc`
- 最终 `git status --short` 中不再出现仓库内 `codex_doc`

## 验证记录

### 红灯验证

执行：

```powershell
python -m pytest tests/unit/test_url_ingest_operation.py -q
```

结果：

- 1 failed, 16 passed
- 失败点：`DEFAULT_TIMEOUT_SECONDS == 10` 断言失败，实际值为 `30`

### 绿灯验证

执行：

```powershell
python -m pytest tests/unit/test_url_ingest_operation.py tests/unit/test_ingest_operation.py -q
```

结果：

```text
30 passed in 4.65s
```

## 未扩展范围确认

- 未实现 CLI 入口扩展
- 未新增 lint 相关改动
- 未修改面向用户的 docs 体系

## 提交建议

- 仅提交：
  - `llm_wiki_core/operations/ingest_url.py`
  - `tests/unit/test_url_ingest_operation.py`
  - `.superpowers/sdd/r3-2-task-3-report.md`
