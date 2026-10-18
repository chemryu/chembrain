# Development — default browser and install-free preview

Frozen pushed source: `aaf4d8b13d4604e98458cd6eec59cc8205254bae`. Baseline6280794 remains historical. Separate Planning completed before implementation. Root owns component/default/build/workflows/docs; separate Development helper owns packager/offline smoke. This is not independent approval.

## Changes

Ordinary npm dev/build now opens molecule-first MolecularLibrary; explicit desktop mode preserves old API UI, setup/start/dev helpers and manual Windows workflow. build:web is cross-platform. Portable mode embeds canonical strict library and generated SVGs through a Vite virtual module, disabling app fetch and external assets. The generated single HTML contains the same app JS/CSS via UTF8/base64 DOM textContent bootstrap, not duplicated app logic or eval. Only four named output files enter an Actions downloadable artifact even if Pages configuration fails. No GitHub PDF/raw-paper upload, visibility/history/main/schedule changes. New @types/node24.10.0 is a pinned build-time typing dependency with lock integrity.

Development portable test discovered a genuine fresh-browser backup-import defect: unchanged starter records took precedence over imported edits. Fixed by tracking whether a library has actually been stored; fresh imports take precedence over initial seed, whereas existing saved edits retain precedence on subsequent imports. Failed storage writes never mark data as saved.

## Actual local checks

Exact-source portable build PASS; 463557bytes, HTML SHA256 `843a7e610582352dfc0e30be310133834684084b20125f89bf894fb5934da10a`; library SHA256 `7853ba5d2b335c274733b8c726ac7b80c899e9d51bfd42295279ea75df2452bb`. Manifest records full source. Source payload150files and portable directory13files PASS. Full Python suite284PASS/1WindowsDPAPISKIP, existing Starlette/httpx deprecation warning. npm ci lock setupPASS. Default dev actual browser25compoundtiles/emptyreactionpanel/noAPI PASS; explicit desktop build and actual browser old-entry fixtureAPI PASS (not Windows EXE proof). Hosted /chembrain/ real-browser full suitePASS before final source freeze; QA reruns changed source.

SingleHTML --http-only actual browserPASS: mocked loopback document with offline/alladditionalresourcesblocked, depictions, molecule filtering, 1DOIcard/authors, all4entityedits, reload, same-browser preservation, fresh-profile exactbackup restoration, invalidimport rejection, read/write/migrationbackupfailures preserve raw originals, mobile, raw-text injection fixture and unexpecteddependency rejection. Local file:// actual test NOTRUN: managed Chromium administrator URL policy blocks file URLs (ERR_BLOCKED_BY_ADMINISTRATOR); no policy was modified or bypassed. Separate GitHubCI executes the actual file test in its normal Playwright browser; required evidence pending.

Environment draft source/install/start instructions updated and saved for this source, requiresPublish=true. No network/secrets changes. Saving a draft does not publish the environment or website.

## Limits

Old quotation/crop blobs remain in prior Git history; remote Actions contents not fully audited, so Public NOTCLEARED. Existing Pages403 is historical pending a new observation. Standalone browser storage depends on filename/path/profile/privacy; BackupJSON before update/move and Importpackage are documented transfer methods. Starter3papers/12draftreactions/49chemicals is partial curated information, unknown structures/conditions remain unknown. No live weekly collection or PC/Box install in this run.

## Actual CI and final Development observations

Exact source CI39102813926 finished: 284PASS/1DPAPISKIP, hosted build/browser and gatesPASS. Actual unflagged file:// portable browser test PASS in normal separate GitHub runner (not local policy bypass), including all edits, fresh-profile restoration, storage failures and malicious fixture. All nine original receipt files are preserved under web/ with byte hashes, immutable receipt8ad7371b089fafad09bfbc222cd565e5cc3a28b5. CI browser-manifest equals local manifest byte-for-byte. Portable artifact upload SUCCESS, artifact12127033101; archive digest reported by Actions, not independently downloaded here. New Pages403 Resource not accessible by integration; deploy/accessSKIP, pageURLnull. CollectionSKIP. Current-source normal npm run build also independently exercised with real local Chromium and temporary root HTTP server: molecule-first initial state, related reactions and no backendAPI PASS; own server stopped. These distinguish ready local preview from blocked website.
