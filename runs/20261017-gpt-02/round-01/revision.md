# Revision — 20261017-gpt-02 / round-01

- Role: separate GPT Revision; no application, test, CI, packaging or source-history edits.
- Reviewed source: `36fde22d2791475062565161bf986b88f035b2da` on `codex/gpt-agent-workflow`.
- Inputs: [Planning](planning.md), [Development](development.md), final [Independent QA](qa.md), implementation and independently executed complementary cases.
- Verdict: **CHANGES REQUESTED**.
- Unresolved findings: **4**. Delivery approval: **NO**. A successful build alone cannot resolve these findings.

## Independent findings and QA dispositions

### REV-01 / QA-01 — HIGH: a PDF redirect loses its article binding

**QA finding confirmed independently.** `server/jacs_collection.py:130` validates only host/HTTPS/public-address constraints in `_Redirect`. The exact DOI check in `_licensed_pdf()` protects the initial supplied URL but is not repeated for redirect destinations.

Revision called the production `redirect_request()` with an original request for `https://pubs.acs.org/doi/pdf/10.1021/jacs.6b00001` and mocked only DNS resolution to one public address. It accepted outgoing requests to both:

```text
https://pubs.acs.org/doi/pdf/10.1021/jacs.different
https://pubs.acs.org/arbitrary-unrelated-route
```

The PDF-byte/parser checks cannot establish the redirected article's identity or whether the original article's license applies. A readable response from the other paper can therefore be saved under the original DOI/license. QA separately reproduced wrong-DOI and non-PDF ACS destinations.

**Required repair:** bind every PDF request and redirect to the original normalized DOI and allowed article-PDF paths, maintaining the matched version and current origin/private-address checks. Reject a wrong DOI or unrelated route before requesting its contents. Add regression coverage of the actual redirect handler, including allowed same-article redirects and rejected wrong-article/non-PDF paths.

### REV-02 / QA-02 — MEDIUM: the saved OA decision cannot be audited

**QA finding confirmed.** `_licensed_pdf()` checks the effective license dates and content-version match, then discards those values by returning only PDF URL and license URL. `_save_pdf()` retains the license URL and fetch time, but not license effective date/version or supplied PDF URL. `_reference()` also validates `journal-article` but drops the upstream type from `collection` metadata.

Revision inspected a saved attachment; its complete key set was:

```text
downloaded_at, filename, license, mtime_ns, page_count, policy,
sha256, size_bytes, source_id
```

**Required repair:** carry the validated license start/end when supplied, content version and supplied matching PDF link into attachment provenance; preserve the Crossref type in collection provenance. Do not replace an existing user's title, citation, notes, DOI/source ID or original upload. Retain public evidence without exposing private paths/full text in ordinary UI summaries or exports.

### REV-03 / QA-03 — MEDIUM: PDF page counts are unbounded

**QA finding confirmed independently.** `server/jacs_collection.py:260` bounds PDF bytes and rejects unreadable/encrypted/empty documents, but accepts every positive page count. Revision generated a valid 1,001-page PDF with PyMuPDF and called the production `_save_pdf()` against temporary fixture storage. It was installed and recorded with `page_count: 1001`. QA's separate helper accepted a valid 10,001-page PDF of about 1 MB. This violates Planning's explicit page-bound requirement even though the byte bound works.

**Required repair:** define a documented maximum page count and check it before staging/installing the attachment. Verify over-limit rejection preserves the bibliographic source, any existing good attachment and citation evidence; record the rejection accurately and leave no partial file. Include boundary coverage without weakening existing byte/magic/parse checks.

### REV-04 / QA-04 — MEDIUM: existing duplicate DOI matches are hidden

**QA finding confirmed independently.** `Store.import_jacs_reference()` preserves duplicate records but silently returns the first preferred source. Revision persisted two separate main sources for the same normalized DOI, then ran `collect_jacs(..., metadata_only=True)` with a fixture gateway. The result was `status: success`, `errors: []`, `existing: 1`; neither a duplicate count nor affected source IDs were reported. QA independently reproduced the same result.

**Required repair:** report duplicate matches with the normalized DOI and retained source IDs/count in collection notices/status while preserving every original record and user field. A deterministic selected source is acceptable; destructive merging or silent ambiguity is not. Verify repeat collection and main/SI distinctions remain correct.

## Verification and remaining gates

Revision's inline reproductions used temporary local storage and generated PDF bytes; no publisher network requests, institutional credentials, model APIs or repository source edits were used. Current HEAD remained the exact reviewed SHA when the report was completed.

Independent QA reran the full local suite (**210 passed, 1 Windows-only skip**) and production build (**PASS**). Those checks do not exercise or resolve the four findings. Development also reports source browser and real-restart checks; Revision does not relabel them as independently executed checks.

At the review checkpoint, exact-source Windows CI is **PENDING**. Its pending status prevents delivery in any case; this negative review does not need to wait for a successful build before requesting concrete repairs. No prior commit's Windows receipt, artifact or approval is transferred to this source.

Public-provider connectivity remains the actually observed **UNAVAILABLE** result reported by Development until later observation establishes otherwise. Deterministic fixtures are not live publisher success. Clean Windows VM and actual user default-browser integration remain **NOT RUN**. Actual user-PC task registration, Box writes/synchronization and live subscription PDF retrieval were not performed or approved.

## Wiki → Planning handoff

Wiki must preserve this complete report and final QA report, record **CHANGES REQUESTED / 4 unresolved findings / no approved deliverable**, and return the four concrete repair tasks to Planning for `round-02`. Planning should retain the original OA-only and user-data-preservation constraints. Development must freeze a new full source SHA after repairs; required local/Windows checks and both independent reviews must then cover that new SHA. Do not return a final candidate to the user or reduce the pass criteria merely because the current tests pass.
