# R4.1 Task 1 进展记录

## 阶段 1：需求与现状确认

- 已完整阅读 `D:\ai\llmWiki\llm-wiki-core\.superpowers\sdd\task-1-brief.md`
- 已确认本任务代码改动范围限定为：
  - `D:\ai\llmWiki\llm-wiki-core\integrations\codex\install\install.ps1`
  - `D:\ai\llmWiki\llm-wiki-core\tests\unit\test_codex_installer_smoke.py`
- 已检查现状：
  - `install.ps1` 当前仅支持 repo-local install
  - `test_codex_installer_smoke.py` 当前尚未覆盖用户级 skill 安装场景
- 已决定按 brief 严格执行 TDD：先补测试并验证 RED，再实现到 GREEN

## 阶段 2：测试先行（RED）

- 已按 brief 在 `D:\ai\llmWiki\llm-wiki-core\tests\unit\test_codex_installer_smoke.py` 追加 3 条 PowerShell 用户级 skill 安装测试：
  - dry-run 不落盘
  - 正常复制 skill
  - 目标目录存在且内容不同时拒绝覆盖
- 已运行 focused pytest：
  - `python -m pytest tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_dry_run_does_not_write_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_copies_skill_to_destination tests/unit/test_codex_installer_smoke.py::test_powershell_user_skill_install_refuses_different_existing_destination -q`
- RED 结果符合预期：
  - `install.ps1` 当前报 `NamedParameterNotFound`
  - 说明缺少 `-InstallUserSkill` / `-SkillDestination` / `-ReplaceUserSkill` 支持

## 阶段 3：实现与验证（GREEN）

- 已在 `D:\ai\llmWiki\llm-wiki-core\integrations\codex\install\install.ps1` 完成用户级 skill 安装实现：
  - 新增参数 `-InstallUserSkill`、`-SkillDestination`、`-ReplaceUserSkill`
  - 保持 repo-local install 兼容；未传 `-InstallUserSkill` 时仍要求 `-VaultPath` 与 `-Purpose`
  - 默认用户级安装目标为 `$HOME\.agents\skills\llm-wiki`
  - 安装前校验源 `SKILL.md` 中包含 `name: llm-wiki` 与 `description:`
  - 支持 dry-run 输出
  - 目标存在且内容不同则拒绝覆盖，并提示 `-ReplaceUserSkill`
  - 目标存在且内容相同则报告已安装
  - 替换时仅删除目标 skill 目录本身
  - 复制后输出两个下一步 Codex prompt 提示
- 已修复一次 PowerShell 解析问题与一次单文件数组比较误判问题
- 已完成验证：
  - focused 新增测试：`3 passed`
  - 全量 `tests/unit/test_codex_installer_smoke.py`：`7 passed, 1 skipped`
