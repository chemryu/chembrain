# Independent QA — 20261017-gpt-02 / round-01

- Role: separate GPT Independent QA; application, tests, CI and source history were not edited.
- Frozen source: `36fde22d2791475062565161bf986b88f035b2da` on `codex/gpt-agent-workflow`.
- Verdict: **CHANGES REQUESTED**. Four unresolved findings below. This source must not be delivered as approved, regardless of its eventual Windows build result.
- Scope: JACS bibliography and explicitly licensed OA PDF collection, source preservation, paper-reference grouping and packaged scheduling. No institutional authentication, subscription PDF retrieval or personal model APIs were used.

## Findings

### QA-01 — HIGH: same-publisher redirects can attach a different paper under the original DOI/license

- Location: `server/jacs_collection.py:130–137`, reached through `CrossrefClient.pdf()` / `_get()`.
- `_licensed_pdf()` correctly checks the initial metadata URL against the article DOI. The redirect handler subsequently checks only public HTTPS origin/credentials/query constraints. It does not retain the original DOI or restrict the redirected path to that article's permitted PDF route.
- Independent reproduction: create `_Redirect({'pubs.acs.org'})`, mock DNS to one public address, and call `redirect_request()` with an initial request for `https://pubs.acs.org/doi/pdf/10.1021/original-article`. Both target URLs below are accepted and returned as outgoing requests:

```text
https://pubs.acs.org/doi/pdf/10.1021/different-article
https://pubs.acs.org/doi/suppl/10.1021/different-article
```

- Actual: if the target returns readable PDF bytes, `_save_pdf()` records them under the original article DOI and license. The same-origin check alone therefore does not establish the matching article/version required by Planning.
- Expected: bind PDF retrieval and every redirect to the original normalized DOI and approved PDF routes/version. Reject wrong-article and non-PDF paths before fetching them; retain the existing public-host/private-address protections. Add a controlled redirect regression that reaches this production handler, rather than checking only other hosts.

### QA-02 — MEDIUM: retained OA evidence omits effective date/version, and bibliographic type is discarded

- Locations: `server/jacs_collection.py:186–236`, `253–257`, `282–288`.
- `_licensed_pdf()` validates license start/end and a content-version match but returns only `(PDF URL, license URL)`. `_save_pdf()` stores license URL and download time, without the applicable license start/end, content version or supplied PDF URL. The imported collection metadata also drops the returned Crossref object type.
- Reproduction: import one fixture article with a current CC-BY license, explicit `vor` link and a known license start. Inspect its attachment metadata and source `collection`: the attachment has `license`/`downloaded_at` but no retained start/version/link evidence, and the collection has journal/authors/date/provider but no `journal-article` type.
- Expected: preserve the validated OA decision evidence and upstream article type without overwriting existing user bibliographic fields or exposing private paths. URL/time alone cannot audit which version was authorized when fetched.

### QA-03 — MEDIUM: downloaded PDFs have no page-count bound

- Location: `server/jacs_collection.py:260–269`.
- `_save_pdf()` checks maximum bytes, PDF magic, readability, encryption and nonzero pages, but accepts any positive page count. Planning explicitly requires both byte and page limits.
- Controlled reproduction by the separate QA transport helper: a structurally valid generated 10,001-page PDF of 1,008,153 bytes is accepted and written, with `page_count: 10001`. Revision independently reproduced acceptance of a 1,001-page PDF. No publisher network access is necessary to reproduce either case.
- Expected: define and enforce a documented maximum page count before installing an attachment. Over-limit files must yield an accurate recorded rejection, preserve the DOI reference and existing attachment, and leave no temporary file.

### QA-04 — MEDIUM: pre-existing duplicate DOI records are silently reused without the promised report

- Location: `server/store.py:74–87`; `server/jacs_collection.py:387–391`.
- Independent reproduction: persist two main-article sources (`original-main`, `second-main`) with the same normalized DOI, then collect matching bibliography with `metadata_only=True`.
- Actual result:

```json
{"duplicate_count": 2, "status": "success", "errors": [], "reported_existing": 1,
 "source_ids": ["original-main", "second-main"]}
```

- Both records are correctly preserved, but the importer arbitrarily returns the first match and provides no duplicate-count or source-ID notice. Planning requires existing duplicate matches to be reported without destructive merging.
- Expected: retain all source IDs/user fields and report the matching duplicates through collection status/notice metadata. A deterministic selected source can still be used; a clean result must not conceal this known ambiguity.

## Independently executed checks

| Check | Result | Evidence |
| --- | --- | --- |
| `.venv/bin/python -m pytest -q` | PASS | 210 passed, 1 Windows-only DPAPI skipped, existing Starlette/httpx deprecation warning; 4.15 seconds. These passing tests do not cover the findings above. |
| `npm run build` | PASS | TypeScript and production frontend completed, 1,726 modules transformed. |
| Controlled production redirect-handler calls | FAIL | Wrong DOI and non-PDF same-publisher redirects accepted, as shown in QA-01. |
| Controlled duplicate-import runtime scenario | FAIL | All original records preserved but no duplicate notice, as shown in QA-04. |
| OA evidence retention and PDF-bound inspection | FAIL | Required persisted fields and explicit page bound missing; helper/Revision independently reproduced the page case. |
| Application/CI/test source modifications by QA | NONE | Only this report is written. |

Development reports additional source browser and real process restart checks passing. Those are implementation-provided evidence, not independently rerun here. Further candidate approval checks are deferred to the corrected source; additional green checks cannot resolve these concrete findings.

## Windows/public-provider evidence and limits

The exact candidate's new Windows CI is pending at this report checkpoint. No previous `3f102821…` receipt is accepted for `36fde22d…`. Windows package build, ordinary EXE/UI/restart/PATH evidence, actual temporary-task registration/removal, headless packaged collection and gateway observation must be inspected again for the corrected exact source before final approval. This report does not wait for CI to request the necessary code fixes.

- Live public gateway: Development observed **UNAVAILABLE** in this cloud. Independent QA has not performed a live PDF download or reclassified that observation as PASS. The Windows observation must preserve its actual provider outcome; deterministic fixtures are not live service success.
- Clean Windows VM and user default-browser registration/integration: **NOT RUN**.
- User-PC schedule installation, local Box writes and Box synchronization: **NOT RUN**; no claim of remote activation is made.
- Public release/deployment: not authorized by this review loop and not performed.

## Next handoff

Send these four findings to Revision, then retain its complete decision through Wiki and return concrete repair tasks to Planning for round-02. Development must commit corrected executable inputs, and both independent reviews plus required checks must target that new full SHA. The present source has no QA approval and no approved deliverable.
