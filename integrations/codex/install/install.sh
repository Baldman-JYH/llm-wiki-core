#!/usr/bin/env sh
set -eu

DRY_RUN=0
INSTALL_USER_SKILL=0
REPLACE_USER_SKILL=0
SKILL_DESTINATION=""

usage() {
  echo "Usage: install.sh [--dry-run] <vault-path> <purpose>" >&2
  echo "       install.sh [--dry-run] [--skill-destination PATH] [--replace-user-skill] --install-user-skill" >&2
}

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"
SKILL_SOURCE="$REPO_ROOT/integrations/codex/skills/llm-wiki"

test_required_content() {
  content_file="$1"
  needle="$2"
  grep -F "$needle" "$content_file" >/dev/null 2>&1
}

test_directories_identical() {
  source_dir="$1"
  destination_dir="$2"

  if [ ! -d "$destination_dir" ]; then
    return 1
  fi

  diff -qr "$source_dir" "$destination_dir" >/dev/null 2>&1
}

show_user_skill_next_prompts() {
  echo "Next Codex prompt: check wiki status"
  echo "Next Codex prompt: search wiki for durable knowledge"
}

install_user_skill() {
  resolved_skill_destination="$SKILL_DESTINATION"
  if [ -z "$resolved_skill_destination" ]; then
    resolved_skill_destination="$HOME/.agents/skills/llm-wiki"
  fi

  skill_manifest="$SKILL_SOURCE/SKILL.md"
  if [ ! -f "$skill_manifest" ]; then
    echo "Codex user skill source manifest not found at \"$skill_manifest\"." >&2
    exit 1
  fi

  if ! test_required_content "$skill_manifest" "name: llm-wiki"; then
    echo "Codex user skill source manifest must contain 'name: llm-wiki'." >&2
    exit 1
  fi

  if ! test_required_content "$skill_manifest" "description:"; then
    echo "Codex user skill source manifest must contain 'description:'." >&2
    exit 1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY RUN: Install Codex user skill from \"$SKILL_SOURCE\" to \"$resolved_skill_destination\""
    return 0
  fi

  if [ -e "$resolved_skill_destination" ]; then
    if [ ! -d "$resolved_skill_destination" ]; then
      echo "Codex user skill destination already exists and differs. Re-run with --replace-user-skill to replace it." >&2
      exit 1
    fi

    if test_directories_identical "$SKILL_SOURCE" "$resolved_skill_destination"; then
      echo "Codex user skill already installed at \"$resolved_skill_destination\""
      show_user_skill_next_prompts
      return 0
    fi

    if [ "$REPLACE_USER_SKILL" -ne 1 ]; then
      echo "Codex user skill destination already exists and differs. Re-run with --replace-user-skill to replace it." >&2
      exit 1
    fi

    rm -rf "$resolved_skill_destination"
  fi

  destination_parent="$(dirname "$resolved_skill_destination")"
  mkdir -p "$destination_parent"
  cp -R "$SKILL_SOURCE" "$resolved_skill_destination"
  echo "Codex user skill installed at \"$resolved_skill_destination\""
  show_user_skill_next_prompts
}

run_or_show() {
  command_text="$1"
  shift
  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY RUN: $command_text"
    return 0
  fi
  echo "$command_text"
  "$@"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --install-user-skill)
      INSTALL_USER_SKILL=1
      shift
      ;;
    --skill-destination)
      if [ "$#" -lt 2 ]; then
        usage
        exit 2
      fi
      SKILL_DESTINATION="$2"
      shift 2
      ;;
    --replace-user-skill)
      REPLACE_USER_SKILL=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    --*)
      usage
      exit 2
      ;;
    *)
      break
      ;;
  esac
done

if [ "$INSTALL_USER_SKILL" -eq 1 ]; then
  install_user_skill
  exit 0
fi

if [ "$#" -lt 2 ]; then
  usage
  exit 2
fi

VAULT_PATH="$1"
PURPOSE="$2"

run_or_show "python3 -m pip install -e \"$REPO_ROOT\"" python3 -m pip install -e "$REPO_ROOT"
run_or_show "llm-wiki init \"$VAULT_PATH\" --purpose \"$PURPOSE\"" llm-wiki init "$VAULT_PATH" --purpose "$PURPOSE"
run_or_show "llm-wiki detect-transport \"$VAULT_PATH\"" llm-wiki detect-transport "$VAULT_PATH"

echo "Next: llm-wiki status \"$VAULT_PATH\""
echo "Next: llm-wiki continue \"$VAULT_PATH\""

echo "llm-wiki Codex adapter initialized for $VAULT_PATH"
