# Planning — 20261017-gpt-02 / round-03

- Status: READY FOR ONE BOUNDED DIAGNOSTIC CYCLE; no delivery approval.
- Prior source: `c96c210a89a077869da78e7e570f06c80768cc16`.
- Published blocked handoff: `71880278222d27e7f6442708411fee647ba647de`.
- Inputs: round-02 [handoff](../round-02/handoff.md), [QA](../round-02/qa.md), [Revision](../round-02/revision.md), and [retained observation](../round-02/windows-pending/observation.json).
- Four prior application findings are independently RESOLVED; unresolved application findings remain **0**. Required Windows evidence is NOT VERIFIED. Do not reopen resolved application scope merely because CI evidence is inaccessible.

## Known facts and scope

At `2026-10-17T07:35:21.810849Z`, the latest observed receipt for run `39011910077` was the initial `running` record, published at `07:04:12Z`, with empty steps and no artifact. Its configured job budget was 30 minutes. Actual terminal runner state remains **UNKNOWN**: elapsed time does not establish timeout, failure, completion or continued execution. GitHub Actions API was Forbidden, including after reconnect. Inspect a late authoritative receipt if one becomes available before source edits, but never promote the start receipt to terminal evidence.

This round changes only CI evidence publication/diagnostics and the independent packaged headless verification path. Preserve JACS publication-window semantics, OA-only policy, original data and all locator provenance, page ceiling, duplicate notices, scheduler behavior, grouped references, and every existing validation gate. No release, automatic merge, default-branch workflow installation, permission change, institutional authentication or personal API key is authorized.

## Development plan

### 1. Source/run-bound stage receipts and bounded diagnostics

- Primary files: `.github/workflows/windows-exe.yml`, `scripts/report_windows_build.sh`, and narrowly scoped supporting receipt/probe scripts/tests as needed.
- Split the current monolithic packaging step into identifiable stages: dependencies, frontend build, Python tests, EXE package, packaged smoke/collector fixture, zero-argument launch/UI/restart/PATH, safe temporary scheduler validation, independent headless CLI, public gateway observation, archive/checksum, artifact upload. Preserve all actual commands and failure propagation.
- Publish before/after stage facts containing full source SHA, run ID, run attempt, run URL, phase, UTC observed/update timestamps, available step outcomes, and artifact/hash only when actually produced. A heartbeat proves only publication/observed phase, never a test pass.
- Give long commands explicit bounded step/subprocess deadlines and preserve useful stage logs incrementally. Choose a finite overall job budget sufficient for all unchanged checks; do not guess that an old run reached its budget or raise budgets indefinitely. Capture bounded tails/bytes per known log, not environment dumps, credentials or paper text. After a failure, later unexecuted checks stay NOT RUN/skipped.
- Use a per-run-and-attempt receipt ref, for example `build/windows-runs/<run-id>-<attempt>`, as the durable authoritative path. Avoid an older cancelled run overwriting a newer candidate's sole receipt. Any optional latest alias is only an index; consumers still verify source/run/attempt and prefer the immutable receipt commit. Keep enough chronological phase evidence to identify the last observed transition.

### 2. Independent terminal reporter in this same workflow

- Add a separate reporter job in **the same existing workflow**, dependent on the Windows build with an appropriate unconditional/always condition and its own finite timeout. A new `workflow_run` workflow on an unmerged feature branch does not satisfy this requirement and is outside the authorized default-branch scope.
- The reporter must not rely solely on the final step inside a build job that may be interrupted. It checks out the triggering source, reads available run-specific checkpoint/evidence and authoritative `needs` job result, and publishes terminal evidence even when build fails or is cancelled, when GitHub schedules that reporter.
- Preserve distinctions: authoritative `failure` is failure, `cancelled` is cancelled; neither is automatically a proven timeout. Record a timeout only when its actual source states that conclusion. Missing step logs/outputs remain unavailable. No artifact URL/checksum or success is fabricated.
- Whole-workflow cancellation, runner/service outage or reporter publication failure can prevent this job from running. In that case retain the last phase and mark final state UNKNOWN/unobserved; this design cannot promise a final report under every platform failure. Receipt write failure must be visible, not silently converted into approval.
- A terminal success receipt requires the unchanged required stage successes and real artifact/hash. A terminal build failure receipt may be useful diagnostic evidence but cannot authorize delivery.

### 3. Unconditional actual packaged headless verification

- Primary files: `scripts/observe_jacs_gateway.py`, a separate deterministic headless-check driver if useful, minimal `scripts/desktop.py` probe support only if required, and focused tests.
- Invoke the actual packaged EXE `--sync-jacs --metadata-only --days 14 --max-pages 1 --data-dir <isolated spaced temporary path>` independently of the preliminary live Crossref probe, including when that probe raises or returns unavailable. Do not substitute the offline fixture inside `--smoke-test` for this invocation.
- Bound the child process, collect actual exit/stdout/stderr safely, parse its result JSON and validate the exit contract: success → 0; bounded partial/provider failure → the documented nonzero result. A hanging, crashing, malformed-output or contract-violating process is a headless verification failure, not an upstream-unavailable success.
- Inspect the temporary SQLite database and result consistency: discovered/saved DOI sources agree, no synthetic seeded app data appears, and metadata-only execution leaves no downloaded PDF. On provider refusal, verify a persisted honest failure/partial outcome and meaningful exit without browser/server launch. Isolated storage means an unexpected already-running result is not accepted as equivalent success.
- Also exercise deterministic **success through the packaged headless CLI branch**, using narrowly scoped, clearly labelled offline fixture injection/probe mode and isolated data rather than changing publisher trust/authentication or production URLs. Validate real SQLite references and expected generated PDF/hash/provenance if that fixture permits PDF collection. Test repeat behavior. A fixture/probe mode must never silently contaminate normal user storage, schedule itself, or masquerade as live retrieval.
- Keep three independent results: deterministic packaged headless success, actual live headless process/exit-contract verification (including legitimate provider-failure behavior), and public provider/PDF observation. Live UNAVAILABLE/UNSUPPORTED is not a live PASS; a missing or skipped invocation is NOT RUN, never inferred from other fixtures.

## Required checks and exact-SHA review

1. Focused receipt tests verify source/run/attempt binding, phase timestamps, bounded/redacted known logs, actual step/outcome preservation, missing artifacts, terminal failure/cancelled versus unknown, and per-run isolation. Inspect same-workflow reporter wiring and ensure receipt/reporting cannot replace failed checks with green heartbeat status.
2. Headless-driver regressions cover initial metadata observation failure while the packaged command still executes, correct success/nonzero-partial contracts, child timeout/crash/malformed JSON, persisted references, and metadata-only PDF absence. Keep fixture versus live observations separate.
3. Run the full Python suite and production frontend build; preserve prior app/browser and data-restart checks. Freeze a new full source SHA because workflow/probe/build inputs changed.
4. Trigger **one bounded diagnostic Windows cycle** for that SHA and inspect run-specific receipts before/after stages, retained logs, terminal reporter outcome, real temporary scheduler registration/inspection/cleanup and actual packaged headless evidence. Never execute collection via a scheduled task. Keep EXE smoke, zero-argument startup, packaged UI, genuine restart retention, restricted Python/Node PATH, collector fixture, and artifact checksum gates.
5. Independent QA and Revision separately inspect the exact corrected SHA and evidence. Wiki preserves full reports. Four resolved app findings remain resolved unless a concrete regression is found; missing Windows evidence remains a blocker rather than an invented app failure.

## Stop and delivery conditions

After this diagnostic cycle, either all required same-source checks and both independent reviews pass with zero unresolved findings and a matching artifact SHA-256, or Wiki records BLOCKED with the actual last observed phase, available terminal result or UNKNOWN, and specific external access/runner/publication limitation. Do not perform endless blind reruns or keep changing source merely to obtain a green receipt. No previous artifact or approval can fill missing current evidence.

Public observations retain actual UNAVAILABLE/UNSUPPORTED results and are not reported as successful live OA download from fixtures. Clean Windows VM, user default-browser integration, user-PC collection/scheduler installation and Box writes/sync remain NOT RUN until performed. No delivery is approved by this plan itself.
