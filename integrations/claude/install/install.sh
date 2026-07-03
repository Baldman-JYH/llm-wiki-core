#!/usr/bin/env sh
set -eu

DRY_RUN=0
INSTALL_PROJECT_ADAPTER=0
REPLACE_CLAUDE_ADAPTER=0
PROJECT_DESTINATION=""

usage() {
  echo "Usage: install.sh --install-project-adapter --project-destination PATH [--dry-run] [--replace-claude-adapter]" >&2
}

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(CDPATH= cd -- "$SCRIPT_DIR/../../.." && pwd)"
CLAUDE_SOURCE="$REPO_ROOT/integrations/claude"

copy_adapter_file() {
  source_file="$1"
  destination_file="$2"

  if [ ! -f "$source_file" ]; then
    echo "Claude adapter source file not found at \"$source_file\"." >&2
    exit 1
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    echo "DRY RUN: Copy \"$source_file\" to \"$destination_file\""
    return 0
  fi

  if [ -e "$destination_file" ]; then
    if [ -f "$destination_file" ] && cmp -s "$source_file" "$destination_file"; then
      return 0
    fi
    if [ "$REPLACE_CLAUDE_ADAPTER" -ne 1 ]; then
      echo "Claude adapter destination already exists and differs. Re-run with --replace-claude-adapter to replace it." >&2
      exit 1
    fi
    if [ ! -f "$destination_file" ]; then
      echo "Claude adapter destination already exists and differs. Re-run with --replace-claude-adapter to replace it." >&2
      exit 1
    fi
    rm -f "$destination_file"
  fi

  destination_parent="$(dirname "$destination_file")"
  mkdir -p "$destination_parent"
  cp "$source_file" "$destination_file"
}

install_project_adapter() {
  if [ -z "$PROJECT_DESTINATION" ]; then
    echo "Claude project adapter install requires --project-destination PATH." >&2
    exit 2
  fi

  if [ ! -d "$PROJECT_DESTINATION" ]; then
    echo "Claude project adapter destination must be an existing directory." >&2
    exit 1
  fi

  echo "Install Claude project adapter into \"$PROJECT_DESTINATION\""

  copy_adapter_file "$CLAUDE_SOURCE/CLAUDE.template.md" "$PROJECT_DESTINATION/CLAUDE.md"
  copy_adapter_file "$CLAUDE_SOURCE/skills/llm-wiki/SKILL.md" "$PROJECT_DESTINATION/.claude/skills/llm-wiki/SKILL.md"
  copy_adapter_file "$CLAUDE_SOURCE/commands/wiki.md" "$PROJECT_DESTINATION/.claude/commands/wiki.md"
  copy_adapter_file "$CLAUDE_SOURCE/commands/save.md" "$PROJECT_DESTINATION/.claude/commands/save.md"

  if [ "$DRY_RUN" -eq 1 ]; then
    return 0
  fi

  echo "Claude project adapter installed at \"$PROJECT_DESTINATION\""
  echo "Next Claude prompt: /wiki status"
  echo "Next Claude prompt: /save"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    --install-project-adapter)
      INSTALL_PROJECT_ADAPTER=1
      shift
      ;;
    --project-destination)
      if [ "$#" -lt 2 ]; then
        usage
        exit 2
      fi
      PROJECT_DESTINATION="$2"
      shift 2
      ;;
    --replace-claude-adapter)
      REPLACE_CLAUDE_ADAPTER=1
      shift
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      usage
      exit 2
      ;;
  esac
done

if [ "$INSTALL_PROJECT_ADAPTER" -ne 1 ]; then
  usage
  exit 2
fi

install_project_adapter
