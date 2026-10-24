#!/usr/bin/env bash
# Skyrim Character Planner - scheduled data refresh.
#  1. Saves fresh copies of the UESP pages the planner uses, and every quest page.
#  2. Rebuilds data/quests.json from the quest pages.
#  3. Checks races, perks and everything else against UESP and writes a report
#     (data/source/CHECK_REPORT.md) of anything new on UESP that the planner lacks.
#  4. Pushes to GitHub.
# If a download fails, nothing is pushed, so a bad run never overwrites good data.
set -uo pipefail

REPO="$HOME/skyrim-planner"
cd "$REPO" || exit 1

echo "=== $(date '+%Y-%m-%d %H:%M') data refresh ==="
git pull --quiet --rebase || { echo "git pull failed; fix the repo first."; exit 1; }

# Use the project's virtual environment if there is one, otherwise system Python
if [ -x .venv/bin/python ]; then PY=.venv/bin/python; else PY=python3; fi

# 1. Downloads: stop here if any fail
"$PY" uesp_ingest.py --dump   || { echo "Page download failed. Nothing was pushed."; exit 1; }
"$PY" uesp_ingest.py --quests || { echo "Quest download failed. Nothing was pushed."; exit 1; }

# 2. Rebuild the quest list
"$PY" scripts/build_quests.py || { echo "Quest rebuild failed. Nothing was pushed."; exit 1; }

# 3. Checks: problems are reported, not fatal
NOTES=""
"$PY" uesp_ingest.py --refresh       || NOTES="$NOTES races"
"$PY" uesp_ingest.py --perks --all --refresh || NOTES="$NOTES perks"
"$PY" scripts/check_data.py
[ -n "$NOTES" ] && echo "Check these against UESP:$NOTES (details above)."

# 4. Push
git add data
if git diff --cached --quiet; then
  echo "No data changes."
else
  git commit --quiet -m "Data refresh $(date +%F)"
  git push --quiet && echo "Pushed new data to GitHub."
fi
