#!/usr/bin/env bash
# Uses Bash 3.2+ and standard macOS/Linux utilities, with no language runtime dependencies.
set -euo pipefail

name=prototype-to-delivery
state=.installation.cksum
payload=(SKILL.md references/design-outline.md references/completion-check.md agents/openai.yaml LICENSE VERSION)
source_dir=$(cd "$(dirname "$0")/.." && pwd -P)
action=${1:-}
[[ $# -eq 0 ]] || shift
platform= dest= work= lock= backup= old_moved=0

fail() { printf 'FAIL %s\n' "$*" >&2; exit 1; }
usage() {
  printf '%s\n' 'Usage: bash scripts/install.sh install|update|reinstall|status' \
    '       (--platform codex|antigravity|antigravity-cli|gemini-cli | --dest /path/prototype-to-delivery)' \
    '       [--source /path/to/source]'
}
case "$action" in
  -h|--help) usage; exit 0 ;;
  install|update|reinstall|status) ;;
  *) usage >&2; exit 2 ;;
esac
while [[ $# -gt 0 ]]; do
  case "$1" in
    --source|--dest|--platform)
      [[ $# -ge 2 && -n "$2" ]] || { usage >&2; exit 2; }
      case "$1" in
        --source) source_dir=$2 ;;
        --dest) [[ -z "$dest$platform" ]] || { usage >&2; exit 2; }; dest=$2 ;;
        --platform) [[ -z "$dest$platform" ]] || { usage >&2; exit 2; }; platform=$2 ;;
      esac
      shift 2 ;;
    *) usage >&2; exit 2 ;;
  esac
done
[[ -n "$dest$platform" ]] || { usage >&2; exit 2; }

if [[ -n "$platform" ]]; then
  case "$platform" in
    codex)
      candidates=("${CODEX_HOME:-$HOME/.codex}/skills/$name" "$HOME/.agents/skills/$name")
      dest=${candidates[1]}
      [[ -z "${CODEX_HOME:-}" ]] || dest=${candidates[0]} ;;
    antigravity) candidates=("$HOME/.gemini/config/skills/$name"); dest=${candidates[0]} ;;
    antigravity-cli) candidates=("$HOME/.gemini/antigravity-cli/skills/$name"); dest=${candidates[0]} ;;
    gemini-cli) candidates=("$HOME/.gemini/skills/$name" "$HOME/.agents/skills/$name"); dest=${candidates[0]} ;;
    *) usage >&2; exit 2 ;;
  esac
  existing=
  for candidate in "${candidates[@]}"; do
    if [[ -e "$candidate" || -L "$candidate" ]]; then
      [[ -z "$existing" || "$existing" == "$candidate" ]] || fail "Multiple installations: $existing, $candidate. Choose --dest explicitly."
      existing=$candidate
    fi
  done
  [[ -z "$existing" ]] || dest=$existing
fi
[[ "$(basename "$dest")" == "$name" ]] || fail "--dest must end in $name"
[[ ! -L "$dest" ]] || fail "Destination is a symlink. Maintain its source instead."

cleanup() {
  local result=$?
  trap - EXIT
  if [[ "$old_moved" == 1 && ! -e "$dest" && ! -L "$dest" ]]; then
    mv "$backup" "$dest" || printf 'FAIL Restore the backup manually: %s\n' "$backup" >&2
  fi
  [[ -z "$work" ]] || rm -rf "$work"
  [[ -z "$lock" ]] || rmdir "$lock"
  exit "$result"
}
trap cleanup EXIT
trap 'exit 130' INT
trap 'exit 143' TERM HUP

valid_version() {
  [[ "$1" =~ ^(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})\.(0|[1-9][0-9]{0,8})$ ]]
}
newer() {
  local a1 a2 a3 b1 b2 b3
  IFS=. read -r a1 a2 a3 <<< "$1"
  IFS=. read -r b1 b2 b3 <<< "$2"
  (( 10#$a1 > 10#$b1 || (10#$a1 == 10#$b1 && 10#$a2 > 10#$b2) ||
     (10#$a1 == 10#$b1 && 10#$a2 == 10#$b2 && 10#$a3 > 10#$b3) ))
}
inventory() {
  local folder=$1 output=$2 item
  (
    cd "$folder"
    find . \( -type f -o -type l \) -print > "$work/file-list"
    while IFS= read -r item; do
      item=${item#./}
      [[ ! -L "$item" ]] || { printf 'Symlink in installation: %s\n' "$item" >&2; exit 1; }
      case "$item" in "$state"|.DS_Store|*/.DS_Store) continue ;; esac
      cksum "$item"
    done < "$work/file-list"
  ) | LC_ALL=C sort > "$output"
}
check_installed() {
  [[ -f "$dest/$state" && ! -L "$dest/$state" ]] || fail "Legacy, manual or damaged installation. Use reinstall to back up and migrate."
  inventory "$dest" "$work/current"
  cmp -s "$work/current" "$dest/$state" || fail "Local changes, missing or added files. Use reinstall only if you want to back up and replace them."
  [[ -f "$dest/VERSION" ]] || fail "Missing installed VERSION. Use reinstall."
  installed_version=$(cat "$dest/VERSION")
  valid_version "$installed_version" || fail "Invalid installed VERSION. Use reinstall."
}

if [[ "$action" == status ]]; then
  [[ -d "$dest" ]] || fail "Installation not found: $dest"
  work=$(mktemp -d "${TMPDIR:-/tmp}/ptd-status.XXXXXX")
  check_installed
  printf 'PASS Installed %s: %s (file checks only; runtime not checked)\n' "$installed_version" "$dest"
  exit 0
fi

source_dir=$(cd "$source_dir" && pwd -P)
for item in "${payload[@]}"; do
  [[ -s "$source_dir/$item" && ! -L "$source_dir/$item" ]] || fail "Missing, empty or linked source file: $item"
done
[[ ! -L "$source_dir/references" && ! -L "$source_dir/agents" ]] || fail "Source resource directories must not be symlinks."
version=$(cat "$source_dir/VERSION")
valid_version "$version" || fail "VERSION must be MAJOR.MINOR.PATCH (at most 9 digits per component)."
mkdir -p "$(dirname "$dest")"
parent=$(cd "$(dirname "$dest")" && pwd -P)
dest="$parent/$name"
case "$dest/" in "$source_dir/"*) fail "Source and destination must be separate." ;; esac
case "$source_dir/" in "$dest/"*) fail "Source and destination must be separate." ;; esac
mkdir "$parent/.$name.install.lock" 2>/dev/null || fail "Installation lock exists: $parent/.$name.install.lock. Remove only after confirming the previous installer has exited."
lock="$parent/.$name.install.lock"
work=$(mktemp -d "$parent/.ptd-install.XXXXXX")
[[ ! -e "$dest" || -d "$dest" ]] || fail "Destination exists but is not a directory."
[[ ! -L "$dest" ]] || fail "Destination became a symlink."
[[ "$action" != update || -d "$dest" ]] || fail "Not installed. Use install first."

# Check only the packaged files; full YAML validation is a separate maintainer check.
(
  cd "$source_dir"
  for item in "${payload[@]}"; do cksum "$item"; done
) | LC_ALL=C sort > "$work/expected"
if [[ -d "$dest" && "$action" != reinstall ]]; then
  check_installed
  if cmp -s "$work/expected" "$dest/$state"; then
    printf 'PASS Already installed %s with identical content.\n' "$version"
    exit 0
  fi
  [[ "$action" == update ]] || fail "Already installed with different content. Use update or reinstall."
  newer "$version" "$installed_version" || fail "Update requires a higher version. Use reinstall for repair or rollback."
fi
if [[ -d "$dest" && "$action" == reinstall ]]; then
  [[ -f "$dest/SKILL.md" || -f "$dest/$state" || -f "$dest/.installation.json" ]] || fail "Destination does not look like a skill installation."
fi

mkdir -p "$work/new/references" "$work/new/agents"
for item in "${payload[@]}"; do cp -p "$source_dir/$item" "$work/new/$item"; done
inventory "$work/new" "$work/copied"
cmp -s "$work/expected" "$work/copied" || fail "Source changed while copying. Existing installation was not changed."
cp "$work/copied" "$work/new/$state"
if [[ -d "$dest" ]]; then
  backups="$(dirname "$parent")/skill-backups/$name"
  mkdir -p "$backups"
  backup=$(mktemp -d "$backups/$(date -u +%Y%m%dT%H%M%SZ).XXXXXX")
  rmdir "$backup"
  printf 'INFO Full backup: %s\n' "$backup"
  mv "$dest" "$backup"
  old_moved=1
fi
mv "$work/new" "$dest"
printf 'PASS %s %s: %s\n' "$action" "$version" "$dest"
printf 'INFO Refresh your host and check skill discovery. No host settings were changed.\n'
