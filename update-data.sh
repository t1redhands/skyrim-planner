#!/usr/bin/env bash
# Skyrim Character Planner - scheduled data refresh.
# Pulls the latest repo, refetches UESP data, and pushes it to GitHub
# only if the run finished cleanly (so a failed fetch never overwrites good data).
set -euo pipefail

REPO="$HOME/skyrim-planner"
cd "$REPO"

echo "=== $(date '+%Y-%m-%d %H:%M') data refresh ==="
git pull --quiet --rebase

# Use the project's virtual environment if there is one, otherwise system Python
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi

if ! "$PY" uesp_ingest.py --refresh; then
  echo "Ingest reported problems (see above). Nothing was pushed."
  exit 1
fi

git add data
if git diff --cached --quiet; then
  echo "No data changes."
else
  git commit --quiet -m "Data refresh $(date +%F)"
  git push --quiet
  echo "Pushed new data to GitHub."
fi
