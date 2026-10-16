# Architecture

The English React/TypeScript interface renders RDKit structures and a React Flow reaction map. FastAPI stores molecules, reactions and references as JSON records in SQLite. Route search walks recorded reaction branches with explicit complexity limits; drafts are excluded by default.

Paper records contain DOI, citation, notes and related-reference IDs. The visible library and reaction inspector use DOI links and page/figure/procedure locators. DOI-only citations are explicitly marked `citation_only`: the server requires a DOI and locator and does not claim a text match. The optional PDF importer retains the stricter page/quote verification for uploaded originals. Original files and extracted text remain local; the app does not render full paper text or put it in Markdown exports.

The PyInstaller desktop launcher bundles the interface, Python runtime, API, RDKit and the curated DOI library. It binds an available loopback port, opens the browser after readiness and saves records in the user's application-data directory. The console window controls the server lifetime. The starter library loads once into a new database. Existing user data is never reset on application updates.

Windows CI runs API tests, builds the EXE on Windows and executes its `--smoke-test` against the bundled UI, API, RDKit and literature data before publishing a release. Linux packaging validation is separate and cannot establish Windows support.
