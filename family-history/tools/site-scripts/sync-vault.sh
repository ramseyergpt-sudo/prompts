#!/bin/bash
# Mirror the Obsidian vault into this Quartz site's content/ folder, leaving out
# private and working material, then prepare the copy for publishing.
# content/ is overwritten on every run: edit notes in the vault, never here.
#
#   VAULT="/path/to/vault" ./scripts/sync-vault.sh
#
# To keep more notes off the site, list them (paths relative to the vault,
# rsync patterns) in scripts/site-exclude.txt, one per line.
set -eu

VAULT="${VAULT:-$HOME/Documents/Obsidian/Family Tree}"
HERE="$(cd "$(dirname "$0")" && pwd)"
DEST="$(cd "$HERE/.." && pwd)/content"
EXTRA=()
[ -f "$HERE/site-exclude.txt" ] && EXTRA=(--exclude-from="$HERE/site-exclude.txt")

mkdir -p "$DEST"
rsync -a --delete --delete-excluded \
  --exclude='.git/' \
  --exclude='.obsidian/' \
  --exclude='.trash/' \
  --exclude='_System/' \
  --exclude='Canvas/' \
  --exclude='Research/Private/' \
  --exclude='originals/' \
  --exclude='*(draft).md' \
  --exclude='*(drafts).md' \
  --exclude='Research/To-do.md' \
  --exclude='Research/Human tasks and blockers.md' \
  --exclude='/CLAUDE.md' \
  --exclude='/AGENTS.md' \
  --exclude='/.gitignore' \
  --exclude='.DS_Store' \
  ${EXTRA[@]+"${EXTRA[@]}"} \
  "$VAULT/" "$DEST/"

# The site's own pages (home page, about page) live in site/ in this repository.
if [ -d "$HERE/../site" ]; then
  cp -R "$HERE/../site/." "$DEST/"
fi

python3 "$HERE/prepare-content.py" "$DEST" "$VAULT"
echo "Synced $(find "$DEST" -name '*.md' | wc -l | tr -d ' ') notes from $VAULT"
