# Development — two-program receiving regressions

- Role: scoped Development helper; not Independent QA or approval.
- Baseline source: `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d` (rejected round-01). New source not yet frozen.
- Owned source: `scripts/paper_workbench_smoke.py` only. No source builds, source commits or other application files edited by this role.

## Changes

Preserved and completed the prior helper's in-progress smoke diff. The real Workbench UI opens an in-memory synthetic private PDF, explicitly checks three chemical structures and two distinct source-recorded solution/stage rows, then downloads strict normalized facts with ordered conditions, quantities, concentration, yield and two evidence locations. No original paper content is committed.

The receiving profiles use saved main libraries with the **same IDs**, not newly-created incoming rows. Cases cover empty stages plus missing structures; partially known conditions and amounts/units; solution/reaction-only updates with all structures already present; empty solution composition; and an existing ordered prefix followed by a genuinely new linked solution/stage. Each verifies a truthful review, no pre-Apply writes, exact formatted original-byte private backup, preserved local notes/aliases/status, complete resulting chemistry, reload and a repeated import with zero primary writes/no extra backup.

Separate real UI receiving cases reject known temperature/time/amount/unit/concentration/yield/basis conflicts, reordered stages, changed composition and changed solute roles without primary or backup writes. Fact-only transaction failures exercise backup quota, backup readback mismatch, primary quota, stale review and an external primary edit during backup; they inspect primary bytes through the original storage method and download the still-visible working library to rule out an unpersisted UI switch. A pre-existing private backup must remain byte-for-byte intact.

Removed an orphaned old handoff block that referenced an already-closed context and wired the new conflict/failure suites into the executable smoke entry point. Keyboard/map checks are owned separately and unchanged here.

## Executed evidence so far

- Python syntax compilation: PASS.
- Real updated two-stage Workbench UI fixture on the previously built `8cbd5fe2fa92da03169922e1cc7a43bb59b0a89d` paper HTML: PASS, offline mocked HTTP with actual local Blob PDF worker. This proves the new synthetic fixture/UI sequence only; it does **not** approve that rejected source or prove the repaired receiving contract.
- Updated full receiving smoke: NOT RUN yet, awaiting the receiver implementation and a rebuilt pair of HTML files.
- Actual `file://` two-program transfer: NOT RUN locally; managed Chromium blocks that scheme. The policy is not bypassed. Fresh exact-source CI remains mandatory.

The root coordinator will record aggregate exact-source build/check results; this report must be supplemented before any delivery claim.
