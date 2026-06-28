# R2 Task 1 报告：Official Obsidian CLI Command Profile And Runner

## 实现内容

本次只完成 Task 1 范围内的命令 profile、runner 边界和导出，不涉及 transport detection、runtime selection 或后续官方 `obsidian` transport 绑定。

已实现内容：

- 新增 `llm_wiki_core/transport/obsidian_cli_runner.py`
- 新增 `ObsidianCliRunResult`
- 新增 `ObsidianCliRunner` 协议
- 新增 `SubprocessObsidianCliRunner`
- 新增 `ObsidianCliProfile`
- 在 `llm_wiki_core/transport/__init__.py` 中导出新符号

`ObsidianCliProfile` 当前提供：

- `help_argv()`
- `read_argv(relative_path)`
- `write_argv(relative_path, content)`
- `append_argv(relative_path, content)`
- `files_argv(root="wiki")`
- `search_argv(query, root="wiki")`

`SubprocessObsidianCliRunner.run(...)` 使用 `subprocess.run(..., capture_output=True, text=True, encoding="utf-8", errors="replace", shell=False, check=False)` 执行命令，并返回 `ObsidianCliRunResult`。

## TDD 记录

### RED

先新增测试文件 `tests/unit/test_obsidian_cli_command_profile.py`，覆盖：

- 官方 Obsidian CLI profile 的 name-value 风格命令构造
- subprocess runner 对 stdout / stderr / returncode 的捕获

RED 验证命令：

```powershell
python -m pytest tests/unit/test_obsidian_cli_command_profile.py -q
```

RED 结果：

- `2 failed`
- 失败原因均为：

```text
ModuleNotFoundError: No module named 'llm_wiki_core.transport.obsidian_cli_runner'
```

### GREEN

随后新增 `llm_wiki_core/transport/obsidian_cli_runner.py` 并更新 `llm_wiki_core/transport/__init__.py` 导出。

GREEN 验证命令：

```powershell
python -m pytest tests/unit/test_obsidian_cli_command_profile.py -q
```

GREEN 结果：

- `2 passed`

### 回归验证

额外复跑：

```powershell
python -m pytest tests/unit/test_obsidian_cli_command_profile.py tests/unit/test_obsidian_cli_transport.py -q
```

结果：

- `3 passed`

## 测试命令与结果

1. `python -m pytest tests/unit/test_obsidian_cli_command_profile.py -q`
   - RED：`2 failed`
   - GREEN：`2 passed`

2. `python -m pytest tests/unit/test_obsidian_cli_command_profile.py tests/unit/test_obsidian_cli_transport.py -q`
   - `3 passed`

## 变更文件

- `llm_wiki_core/transport/obsidian_cli_runner.py`
- `llm_wiki_core/transport/__init__.py`
- `tests/unit/test_obsidian_cli_command_profile.py`
- `codex_doc/task-1-progress.md`
- `.superpowers/sdd/task-1-report.md`

## 自检结果

- 已按 TDD 执行：先写测试，再看失败，再实现，再验证通过
- 新增测试覆盖了命令 profile 和 subprocess runner 的核心行为
- 旧的 `ObsidianCliTransport` 边界测试未受影响
- 导出层已能通过 `llm_wiki_core.transport` 访问新符号
- 代码改动保持在 Task 1 指定范围内，没有修改其他任务文件

## 疑虑

- 当前只完成“命令 profile、runner 边界和导出”，还没有实现后续任务中的 transport 运行时选择、检测或更高层整合
- `ObsidianCliProfile.timeout_seconds` 已按需求保留，但本任务不负责将其接入上层调用链
