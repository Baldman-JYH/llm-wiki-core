# R2.1 Documentation Consistency Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Align public documentation with the completed R2 official `obsidian` CLI runtime boundary without changing runtime behavior.

**Architecture:** This is a documentation-only release pass. Add guard tests that fail on stale pre-R2 Obsidian CLI wording, update public docs to say official `obsidian` is optional and verified-only, then verify no runtime code changed. Historical milestone plans and specs stay historical unless they are current public guidance.

**Tech Stack:** Markdown docs, pytest documentation guard tests, Python pathlib/re.

## Global Constraints

- Karpathy LLM Wiki gist remains the abstract design source.
- `claude-obsidian` remains the reference implementation, not code to copy.
- `llm-wiki-core` remains neutral across Codex, Claude Code, and future local agents.
- R2.1 is documentation-only.
- Do not change runtime, detection, transport, CLI, or operation code.
- Do not add URL ingest, batch ingest, deep retrieval, BM25, vector search, or LLM synthesis.
- Do not change `D:/ai/llmWiki/claude-obsidian`.
- Do not move `v0.1.0-mvp`.
- Do not claim Obsidian CLI is required.
- Do not claim Obsidian CLI is the default runtime.
- Git commit messages must be Chinese.

---

## File Structure

- `tests/unit/test_r2_obsidian_cli_docs.py`
  - Extend public-doc corpus and stale wording guards for R2.1.
- `tests/unit/test_readme_hygiene.py`
  - Tighten README guard against pre-R2 Obsidian CLI implementation wording.
- `README.md`
  - Update front-page capabilities and current boundaries.
- `docs/roadmap.md`
  - Move Obsidian CLI actual read/write/search out of future roadmap wording now that R2 is complete.
- `docs/completion-criteria.md`
  - Update completion boundary wording to distinguish MVP tag history from current `main`.
- `docs/release-readiness-checklist.md`
  - Keep MVP checklist historical, but add an R2 note so current readers are not misled.
- `docs/artifact-equivalence-verification.md`
  - Update current verification boundary wording for R2.
- `docs/obsidian-cli-transport-boundary-rehearsal.md`
  - Mark the rehearsal as historical MVP/R1 boundary evidence and point readers to the R2 report for current behavior.
- `docs/reference-implementation-alignment.md`
  - Update transport fallback language to R2 verified-only wording.
- `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`
  - External progress record only. Do not add this file to the repo.

---

### Task 1: Public Documentation Consistency

**Files:**
- Modify: `tests/unit/test_r2_obsidian_cli_docs.py`
- Modify: `tests/unit/test_readme_hygiene.py`
- Modify: `README.md`
- Modify: `docs/roadmap.md`
- Modify: `docs/completion-criteria.md`
- Modify: `docs/release-readiness-checklist.md`
- Modify: `docs/artifact-equivalence-verification.md`
- Modify: `docs/obsidian-cli-transport-boundary-rehearsal.md`
- Modify: `docs/reference-implementation-alignment.md`

**Interfaces:**
- Consumes: Existing `_read(relative: str) -> str`, `_public_docs_corpus() -> str`, and README hygiene tests.
- Produces: Public docs that reflect R2 verified-only official `obsidian` behavior and tests that prevent stale pre-R2 wording from returning.

- [ ] **Step 1: Extend the public-doc corpus**

Modify `PUBLIC_DOCS` in `tests/unit/test_r2_obsidian_cli_docs.py` to include the current public docs that R2.1 is allowed to update:

```python
PUBLIC_DOCS = (
    "README.md",
    "docs/user-guide.md",
    "docs/transport-contract.md",
    "docs/r2-obsidian-cli-transport-report.md",
    "docs/roadmap.md",
    "docs/completion-criteria.md",
    "docs/release-readiness-checklist.md",
    "docs/artifact-equivalence-verification.md",
    "docs/obsidian-cli-transport-boundary-rehearsal.md",
    "docs/reference-implementation-alignment.md",
)
```

- [ ] **Step 2: Add stale wording guard**

Append this test to `tests/unit/test_r2_obsidian_cli_docs.py`:

```python
def test_public_docs_do_not_claim_r2_obsidian_runtime_is_unimplemented() -> None:
    corpus = _public_docs_corpus()
    stale_fragments = [
        "Actual Obsidian CLI read/write/search is not implemented",
        "actual Obsidian CLI read/write/search is not implemented",
        "actual read/write/search through Obsidian CLI remains outside the MVP",
        "actual read/write/search 实现前不作为 runtime preferred",
        "Actual Obsidian CLI read / write / search integration",
        "Obsidian CLI actual read/write/search",
    ]

    for fragment in stale_fragments:
        assert fragment not in corpus
```

- [ ] **Step 3: Add R2 verified-only wording guard**

Append this test to `tests/unit/test_r2_obsidian_cli_docs.py`:

```python
def test_public_docs_describe_obsidian_cli_as_optional_verified_runtime() -> None:
    corpus = _public_docs_corpus()

    assert "official `obsidian` CLI" in corpus
    assert "filesystem fallback" in corpus
    assert "read/write/append/list/search" in corpus
    assert "capability probe" in corpus
    assert "legacy `obsidian-cli`" in corpus
```

- [ ] **Step 4: Tighten README hygiene**

Replace the `forbidden_fragments` list in `tests/unit/test_readme_hygiene.py` with:

```python
    forbidden_fragments = [
        "canonical pattern",
        "full `claude-obsidian` parity",
        "preferred runtime",
        "actual read/write/search",
        "实际读写与搜索能力实现前",
        "尚未实现 Obsidian CLI 的实际读写与搜索调用",
        "D:/ai/llmWiki",
    ]
```

Then append this assertion block to `test_readme_avoids_internal_status_jargon`:

```python
    assert "official `obsidian` CLI" in readme
    assert "filesystem fallback" in readme
    assert "验证通过" in readme
```

- [ ] **Step 5: Verify red**

Run:

```powershell
python -m pytest tests/unit/test_r2_obsidian_cli_docs.py tests/unit/test_readme_hygiene.py -q
```

Expected before documentation edits:

- At least one failure from stale README wording about Obsidian CLI implementation.
- At least one failure from stale public docs listed in `PUBLIC_DOCS`.

- [ ] **Step 6: Update README capabilities**

In `README.md`, replace:

```markdown
- 使用 `filesystem` 作为当前已实现的运行通道。
- 检测 Obsidian CLI 是否存在，但在其实际读写与搜索能力实现前，不把它作为默认运行通道。
```

with:

```markdown
- 使用 `filesystem` 作为稳定、可移植的运行通道。
- 支持 official `obsidian` CLI 的可选运行通道；只有在 vault binding 与 read/write/append/list/search capability probe 全部通过后才会启用，否则继续 filesystem fallback。
```

- [ ] **Step 7: Update README current boundaries**

In `README.md`, replace:

```markdown
- 尚未实现 Obsidian CLI 的实际读写与搜索调用。
- 尚未覆盖 `claude-obsidian` 的全部高级能力。
```

with:

```markdown
- Obsidian CLI 不是必需项；official `obsidian` CLI 仅在验证通过后作为可选运行通道启用，未验证时继续 filesystem fallback。
- 尚未覆盖 `claude-obsidian` 的全部高级能力。
```

- [ ] **Step 8: Update README roadmap line**

In `README.md`, replace:

```markdown
- R2：实现并验证 Obsidian CLI 通道。
```

with:

```markdown
- R2：已完成，official `obsidian` CLI 通道采用 verified-only 策略并保留 filesystem fallback。
```

- [ ] **Step 9: Update roadmap transport wording**

In `docs/roadmap.md`, replace:

```markdown
- Obsidian CLI actual read/write/search.
```

with:

```markdown
- Obsidian CLI integration hardening after R2 verified-only runtime selection.
```

Replace:

```markdown
The current runtime remains filesystem until another transport is implemented and verified.
```

with:

```markdown
The portable baseline remains filesystem. The official `obsidian` CLI is optional and can be selected only after verification succeeds.
```

- [ ] **Step 10: Update completion criteria**

In `docs/completion-criteria.md`, replace:

```markdown
- Obsidian CLI actual read/write/search is not implemented.
- Obsidian CLI detection may record availability, but it does not become runtime preferred until actual read/write/search exists.
```

with:

```markdown
- R2 adds an optional official `obsidian` CLI runtime path.
- The official `obsidian` CLI is selected only after vault binding and read/write/append/list/search capability probes pass; otherwise filesystem fallback remains active.
```

Replace any later `Actual Obsidian CLI read/write/search.` future-work bullet with:

```markdown
- Obsidian CLI runtime hardening beyond the R2 verified-only path.
```

- [ ] **Step 11: Update release readiness checklist**

In `docs/release-readiness-checklist.md`, replace:

```markdown
- [x] Obsidian CLI actual read/write/search is not implemented and is documented as a boundary.
```

with:

```markdown
- [x] MVP release notes document that Obsidian CLI was not required for `v0.1.0-mvp`.
- [x] R2 documentation now records the verified-only official `obsidian` CLI runtime path.
```

Replace:

```markdown
- [ ] Actual Obsidian CLI read/write/search.
```

with:

```markdown
- [ ] Obsidian CLI runtime hardening beyond the R2 verified-only path.
```

- [ ] **Step 12: Update artifact equivalence verification**

In `docs/artifact-equivalence-verification.md`, replace:

```markdown
- Actual Obsidian CLI read/write/search is not implemented.
```

with:

```markdown
- Official `obsidian` CLI transport is optional and verified-only; filesystem remains the artifact-equivalence baseline.
```

- [ ] **Step 13: Update Obsidian CLI boundary rehearsal**

At the top of `docs/obsidian-cli-transport-boundary-rehearsal.md`, after the title, add:

```markdown
> Historical note: this rehearsal documents the MVP/R1 boundary before R2. Current R2 behavior is documented in `docs/r2-obsidian-cli-transport-report.md`: official `obsidian` CLI can be runtime eligible only after vault binding and read/write/append/list/search capability probes pass.
```

Then replace:

```markdown
The current reliable runtime transport is filesystem. Obsidian CLI can be detected and recorded, but actual read/write/search through Obsidian CLI remains outside the MVP.
```

with:

```markdown
For the original MVP boundary, the reliable runtime transport was filesystem. After R2, the official `obsidian` CLI is optional and verified-only, while filesystem remains the fallback.
```

Replace:

```markdown
`ObsidianCliTransport` exists only as a contract placeholder. Its methods raise `ObsidianCliTransportNotImplementedError` until actual Obsidian CLI read/write/search behavior is implemented and tested.
```

with:

```markdown
This historical rehearsal predates the R2 `ObsidianCliTransport` implementation. R2 replaced the placeholder with a fake-runner-tested transport that is selected only after capability verification.
```

- [ ] **Step 14: Update reference implementation alignment**

In `docs/reference-implementation-alignment.md`, replace:

```markdown
- transport fallback：当前以 filesystem 作为已实现 runtime transport；Obsidian CLI 可检测、可记录，actual read/write/search 实现完成后再成为可选增强通道。
```

with:

```markdown
- transport fallback：filesystem 仍是稳定兜底通道；official `obsidian` CLI 是可选 verified-only 通道，只有 vault binding 与 read/write/append/list/search capability probe 全部通过后才会启用。
```

- [ ] **Step 15: Verify green**

Run:

```powershell
python -m pytest tests/unit/test_r2_obsidian_cli_docs.py tests/unit/test_readme_hygiene.py -q
```

Expected:

- All tests pass.

- [ ] **Step 16: Commit tests and documentation edits**

Run:

```powershell
git add tests/unit/test_r2_obsidian_cli_docs.py tests/unit/test_readme_hygiene.py README.md docs/roadmap.md docs/completion-criteria.md docs/release-readiness-checklist.md docs/artifact-equivalence-verification.md docs/obsidian-cli-transport-boundary-rehearsal.md docs/reference-implementation-alignment.md
git commit -m "修正 R2.1 公开文档一致性"
```

---

### Task 2: Final Verification, Progress Record, Merge, And Push

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`

**Interfaces:**
- Consumes: Task 1 commit.
- Produces: verified R2.1 completion record and remote `main` update.

- [ ] **Step 1: Run focused documentation tests**

Run:

```powershell
python -m pytest tests/unit/test_r2_obsidian_cli_docs.py tests/unit/test_readme_hygiene.py -q
```

Expected:

- All focused documentation tests pass.

- [ ] **Step 2: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected:

- All tests pass.
- The existing Windows POSIX shell dry-run skip remains acceptable.

- [ ] **Step 3: Check reference repo remains untouched**

Run:

```powershell
git -C D:\ai\llmWiki\claude-obsidian status --short --branch
```

Expected:

```text
## main...origin/main
```

- [ ] **Step 4: Check no runtime code changed**

Run:

```powershell
git diff --name-only main..HEAD
```

Expected changed paths are documentation and tests only:

```text
README.md
docs/artifact-equivalence-verification.md
docs/completion-criteria.md
docs/obsidian-cli-transport-boundary-rehearsal.md
docs/reference-implementation-alignment.md
docs/release-readiness-checklist.md
docs/roadmap.md
docs/superpowers/plans/2026-06-28-r2-1-doc-consistency.md
docs/superpowers/specs/2026-06-28-r2-1-doc-consistency-design.md
tests/unit/test_r2_obsidian_cli_docs.py
tests/unit/test_readme_hygiene.py
```

- [ ] **Step 5: Clean test cache**

Run:

```powershell
if (Test-Path -LiteralPath .pytest_cache) {
  $root = (Resolve-Path -LiteralPath .).Path
  $target = (Resolve-Path -LiteralPath .pytest_cache).Path
  if (-not $target.StartsWith($root)) { throw "Refusing to remove path outside repo: $target" }
  Remove-Item -LiteralPath $target -Recurse -Force
}
```

- [ ] **Step 6: Update external progress document**

Append a new stage to `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`:

```markdown
## 阶段 70：R2.1 Documentation Consistency Implementation

状态：已完成

### 本阶段目标

完成 R2.1 文档一致性收尾，使公开文档与 R2 official `obsidian` CLI verified-only runtime 行为一致。

### 验证结果

- Focused docs tests：记录实际 pass 数。
- Full suite：记录实际 pass/skip 数。
- `claude-obsidian`：确认无修改。
- `v0.1.0-mvp` tag：确认未移动。

### Git 结果

- R2.1 branch：`r2-1-doc-consistency`
- Final commit：记录实际 commit。
- Remote main：记录实际 hash。
```

Do not add this external file to the repo.

- [ ] **Step 7: Merge to main and push**

Run:

```powershell
git checkout main
git pull --ff-only
git merge --ff-only r2-1-doc-consistency
python -m pytest -q
git push origin main
git branch -d r2-1-doc-consistency
```

Expected:

- Merge is fast-forward.
- Post-merge tests pass.
- `origin/main` advances to the R2.1 final commit.
- Local R2.1 branch is deleted.

- [ ] **Step 8: Final status checks**

Run:

```powershell
git status --short --branch
git log --oneline --decorate -5
git ls-remote --heads --tags origin
git -C D:\ai\llmWiki\claude-obsidian status --short --branch
```

Expected:

- `llm-wiki-core` is clean on `main...origin/main`.
- `claude-obsidian` is clean.
- `refs/heads/main` points to the R2.1 final commit.
- `refs/tags/v0.1.0-mvp^{}` still points to `e19162c7ba03b81dfec56815b17e03e20086352f`.
