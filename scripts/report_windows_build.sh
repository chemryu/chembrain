#!/usr/bin/env bash
# CI-only build receipt: readable through authenticated Git when the Actions API is unavailable.
set -euo pipefail
: "${GITHUB_WORKSPACE:?This script runs inside GitHub Actions}"
: "${RUNNER_TEMP:?This script runs inside GitHub Actions}"
export BUILD_RESULT="${1:?Pass the build state}"
report_dir="$RUNNER_TEMP/chembrain-build-receipt"
mkdir -p "$report_dir"
cd "$report_dir"
git init -b build/windows-status
git config user.name 'github-actions[bot]'
git config user.email '41898282+github-actions[bot]@users.noreply.github.com'
python - <<'PY'
import json, os
from pathlib import Path
repo = os.environ['GITHUB_REPOSITORY']
run_id = os.environ['GITHUB_RUN_ID']
build = os.environ['GITHUB_RUN_NUMBER']
Path('status.json').write_text(json.dumps({
    'status': os.environ['BUILD_RESULT'], 'commit': os.environ['GITHUB_SHA'],
    'run_url': f'https://github.com/{repo}/actions/runs/{run_id}',
    'release_url': f'https://github.com/{repo}/releases/tag/windows-{build}',
    'steps': {name: step.get('outcome') for name, step in json.loads(os.environ.get('BUILD_STEPS', '{}')).items()}
}, indent=2), encoding='utf-8')
PY
for stage in dependencies interface api packaging packaged-smoke publication; do
  if [[ -f "$GITHUB_WORKSPACE/$stage.log" ]]; then
    tail -200 "$GITHUB_WORKSPACE/$stage.log" > "$stage.log"
  fi
done
git add status.json ./*.log 2>/dev/null || git add status.json
git commit -m "Windows build $GITHUB_RUN_NUMBER: $BUILD_RESULT"
git -C "$GITHUB_WORKSPACE" fetch "$report_dir" build/windows-status
git -C "$GITHUB_WORKSPACE" push origin FETCH_HEAD:refs/heads/build/windows-status --force
