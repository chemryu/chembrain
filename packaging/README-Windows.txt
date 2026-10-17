Chembrain for Windows 10/11 (64-bit)
REVIEW CANDIDATE - not an approved release

1. Extract the downloaded ZIP to a folder.
2. Double-click Chembrain.exe. The first launch can take a little longer while the app unpacks.
3. Your browser opens automatically. Keep the Chembrain console window open while using the app.
4. Close that console window or press Ctrl+C to stop Chembrain.

The package bundles its Python runtime and compiled frontend. Runtime PATH isolation is tested; a clean Windows VM test remains pending.
The app starts with 14 molecules and 6 curated reactions from three papers.
Paper references open through DOI links. Full papers are not included.
Reaction references from the same DOI appear once, retaining main/SI evidence locations.
Four records are reviewed; two Nicewicz entries remain drafts because article/SI yields differ.
Review status describes the record, not independent experimental reproduction.

Your records are saved in %LOCALAPPDATA%\Chembrain, independently of the EXE.
Keep that folder when updating; back it up to preserve your database.
Export Markdown in the app saves reaction notes and DOI citations without paper text.
If the browser does not open, use the local address printed in the console window.

JACS weekly collection:
Open Paper library. Collect now retrieves public bibliography and only PDFs with
verified current open licenses and same-DOI ACS links (including redirects).
Downloads are capped at 30 MB and 400 pages; license provenance is kept locally.
Duplicate existing main records are preserved and reported in collection notices.
Some open PDFs may lack
the metadata needed for automatic collection. Subscription PDFs remain DOI links
for normal campus/VPN access; this collector does not request your credentials.
Saved open PDFs: %LOCALAPPDATA%\Chembrain\jacs_pdfs
Enable Weekly collection, choose a day/time and Save weekly schedule to activate
a current-user Windows task. Default: Monday 09:00, this PC's local time.
Keep the PC on, online and logged in; the app may be closed. Missed runs start
when available. Disable the checkbox and save to remove the task.
No task is installed until you enable it locally. Paper imports do not create
automatically reviewed reactions. No GPT/Claude API key is used.

This build is not code-signed. Windows may show a publisher warning.
This candidate is an Actions artifact from chemryu/chembrain. Independent review is required before release.
The old windows-3 release has a known ordinary-startup bug.
Default-browser requests use a shell probe in CI; Playwright tests the packaged UI separately.
