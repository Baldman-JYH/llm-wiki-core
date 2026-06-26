#!/usr/bin/env sh
set -eu

DRY_RUN=0
if [ "${1:-}" = "--dry-run" ]; then
  DRY_RUN=1
  shift
fi

if [ "$#" -lt 2 ]; then
  echo "Usage: install.sh [--dry-run] <vault-path> <purpose>" >&2
  exit 2
fi

VAULT_PATH="$1"
PURPOSE="$2"
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"

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

run_or_show "python3 -m pip install -e \"$REPO_ROOT\"" python3 -m pip install -e "$REPO_ROOT"
run_or_show "llm-wiki init \"$VAULT_PATH\" --purpose \"$PURPOSE\"" llm-wiki init "$VAULT_PATH" --purpose "$PURPOSE"
run_or_show "llm-wiki detect-transport \"$VAULT_PATH\"" llm-wiki detect-transport "$VAULT_PATH"

echo "Next: llm-wiki status \"$VAULT_PATH\""
echo "Next: llm-wiki continue \"$VAULT_PATH\""

echo "llm-wiki Codex adapter initialized for $VAULT_PATH"
