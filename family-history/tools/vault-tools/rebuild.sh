#!/bin/bash
# Rebuild every generated view in the vault, then run the health check.
# Run at the end of every session:  bash "_System/tools/rebuild.sh"
set -e
T="$(cd "$(dirname "$0")" && pwd)"
V="${1:-$(cd "$T/../.." && pwd)}"
for s in recompute canvases timeline completeness migration descent backlinks todo; do
  python3 "$T/$s.py" "$V"
done
python3 "$T/check.py" "$V"
