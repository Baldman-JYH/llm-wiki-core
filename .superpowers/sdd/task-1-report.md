# R4.1 Task 1 Report

## 任务

PowerShell User-Level Skill Install

## 实现摘要

- 在 `D:\ai\llmWiki\llm-wiki-core\integrations\codex\install\install.ps1` 中新增用户级 skill 安装参数：
  - `-InstallUserSkill`
  - `-SkillDestination`
  - `-ReplaceUserSkill`
- 保持 repo-local install 兼容：
  - 未传 `-InstallUserSkill` 时，仍要求同时提供 `-VaultPath` 与 `-Purpose`
  - 原有 dry-run 输出仍保留 `pip install -e`、`llm-wiki init`、`llm-wiki detect-transport`、`llm-wiki status`、`llm-wiki continue`
- 用户级 skill 安装行为：
  - 源目录固定为 `integrations/codex/skills/llm-wiki`
  - 默认目标目录为 `$HOME/.agents/skills/llm-wiki`
  - 校验源 `SKILL.md` 含 `name: llm-wiki` 与 `description:`
  - `-DryRun` 时仅输出安装计划，不落盘
  - 目标存在且内容相同则报告已安装
  - 目标存在且内容不同则拒绝覆盖，并提示使用 `-ReplaceUserSkill`
  - `-ReplaceUserSkill` 仅删除目标 skill 目录本身，再执行复制
  - 安装完成后输出：
    - `Next Codex prompt: check wiki status`
    - `Next Codex prompt: search wiki for durable knowledge`

## TDD 记录

### RED

先在 `D:\ai\llmWiki\llm-wiki-core\tests\unit\test_codex_installer_smoke.py` 中新增 3 条测试：

- `test_powershell_user_skill_install_dry_run_does_not_write_destination`
- `test_powershell_user_skill_install_copies_skill_to_destination`
- `test_powershell_user_skill_install_refuses_different_existing_destination`

运行：

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_dry_run_does_not_write_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_copies_skill_to_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_refuses_different_existing_destination -q
```

结果：3 条测试失败，失败原因为 `install.ps1` 尚不支持新增参数，符合 brief 预期。

### GREEN

完成 `install.ps1` 最小实现后，重新运行同一组 focused tests：

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_dry_run_does_not_write_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_copies_skill_to_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_refuses_different_existing_destination -q
```

结果：`3 passed`

## 验证

运行 brief 指定聚焦测试：

```powershell
python -m pytest tests/unit/test_codex_installer_smoke.py -q
```

结果：

- `7 passed`
- `1 skipped`

跳过项为 POSIX shell dry-run 测试，仅在非 Windows 平台执行，符合现有测试约束。

## 变更文件

- `D:\ai\llmWiki\llm-wiki-core\integrations\codex\install\install.ps1`
- `D:\ai\llmWiki\llm-wiki-core\tests\unit\test_codex_installer_smoke.py`

## 风险与说明

- 本次未修改 global Codex config
- 本次未引入 WSL 或 Git Bash 依赖
- 目录内容一致性判定基于递归文件相对路径与 SHA256 指纹比较
