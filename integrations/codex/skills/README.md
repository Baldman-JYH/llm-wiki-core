# Codex Skills

The reusable LLM Wiki skill lives in `integrations/codex/skills/llm-wiki`.

## User-Level Installation

Copy the `llm-wiki` skill directory into the Codex user skills directory for your platform.

The documented default destination is:

```text
$HOME/.agents/skills/llm-wiki
```

Use the installer when possible so user-level installation stays explicit:

- PowerShell: `.\install.ps1 -InstallUserSkill`
- Shell: `./install.sh --install-user-skill`

R4.1 keeps repo-local install available and does not automatically mutate global Codex configuration.

## Verification

Verify `SKILL.md` contains `name: llm-wiki`.

Verify the skill includes `llm-wiki search`, `llm-wiki ingest-batch`, and `llm-wiki ingest-url`.

Then ask Codex to:

- "check wiki status"
- "continue wiki"
- "search wiki for durable knowledge"
- "what does the wiki know about durable knowledge"
