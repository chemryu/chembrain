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
    'release_published': False, 'independent_review_required': True,
    'artifact_url': json.loads(os.environ.get('BUILD_STEPS', '{}')).get('artifact', {}).get('outputs', {}).get('artifact-url'),
    'limits': ['No clean Windows VM test; runtime isolation removes Python/Node from the EXE PATH.', 'Browser opening uses a shell probe; Playwright separately tests the packaged UI.'],
    'steps': {name: step.get('outcome') for name, step in json.loads(os.environ.get('BUILD_STEPS', '{}')).items()}
}, indent=2), encoding='utf-8')
PY
for stage in dependencies interface api packaging packaged-smoke normal-launch jacs-schedule publication; do
  if [[ -f "$GITHUB_WORKSPACE/$stage.log" ]]; then
    tail -200 "$GITHUB_WORKSPACE/$stage.log" > "$stage.log"
  fi
done
if [[ -f "$GITHUB_WORKSPACE/jacs-gateway.json" ]]; then
  cp "$GITHUB_WORKSPACE/jacs-gateway.json" jacs-gateway.json
fi
if [[ -f "$GITHUB_WORKSPACE/SHA256SUMS.txt" ]]; then
  cp "$GITHUB_WORKSPACE/SHA256SUMS.txt" SHA256SUMS.txt
fi
git add .
git commit -m "Windows build $GITHUB_RUN_NUMBER: $BUILD_RESULT"
git -C "$GITHUB_WORKSPACE" fetch "$report_dir" build/windows-status
git -C "$GITHUB_WORKSPACE" push origin FETCH_HEAD:refs/heads/build/windows-status --force
