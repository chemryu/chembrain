"""Read-only browser checks against the actual imported literature workspace.

Requires Playwright and Chromium in the invoking Python environment.
The application must already be running on port 8000.
"""
import json
import os
import shutil
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    report = json.loads((ROOT / ".data/curations/uploaded-literature-report.json").read_text())
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or shutil.which("chromium"), args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto("http://127.0.0.1:8000", wait_until="networkidle")
        expect(page.get_by_role("checkbox", name="데모 포함")).not_to_be_checked()
        expect(page.locator(".molecule-node")).to_have_count(14)
        expect(page.locator(".reaction-node")).to_have_count(6)
        page.get_by_label("논문 필터", exact=True).select_option("10.1038/nature17431")
        expect(page.locator(".molecule-node")).to_have_count(4)
        expect(page.locator(".reaction-node")).to_have_count(2)
        page.locator(".reaction-node").filter(has_text="tert-butyl (6)").click()
        expect(page.locator(".inspector .conditions")).to_contain_text("MeCN 3 mL")
        expect(page.locator(".inspector .conditions")).to_contain_text("52%")
        page.screenshot(path="/tmp/chembrain-literature.png", full_page=True)
        page.locator(".evidence-card").filter(has_text="화합물 6").click()
        expect(page.get_by_label("원문 페이지", exact=True)).to_have_value("45")
        expect(page.locator(".source-text")).to_contain_text("MeCN (3 mL)")
        expect(page.get_by_role("link", name="원본 열기")).to_have_attribute("href", f"/api/sources/{report['source_ids']['41586_2016_BFnature17431_MOESM219_ESM.pdf']}/file#page=45")
        expect(page.locator(".source-doi")).to_contain_text("10.1038/nature17431")
        page.get_by_placeholder("자료 안에서 찾기").fill("Phenyl cyclohexenone")
        page.locator(".source-search-results > button").filter(has_text="PDF p.45").click()
        expect(page.get_by_label("원문 페이지", exact=True)).to_have_value("45")
        page.locator(".linked-sources button").filter(has_text="Horn 2016 · 본문").click()
        expect(page.get_by_role("heading", name="Horn 2016 · 본문", exact=True)).to_be_visible()
        expect(page.get_by_label("원문 페이지", exact=True)).to_have_value("1")
        page.get_by_role("button", name="서지 정보 편집", exact=True).click()
        expect(page.locator('.source-metadata-form input[name="doi"]')).to_have_value("10.1038/nature17431")
        page.get_by_role("button", name="서지 정보 접기", exact=True).click()
        page.get_by_role("button", name="반응 지도", exact=True).click()
        page.get_by_label("논문 필터", exact=True).select_option("10.1126/science.1161976")
        expect(page.locator(".reaction-node")).to_have_count(2)
        page.locator(".reaction-node").filter(has_text="entry 3").click()
        expect(page.locator(".inspector .badge")).to_contain_text("검토 전 초안")
        expect(page.locator(".inspector")).to_contain_text("92% yield, 90% ee")
        page.get_by_role("button", name="경로 탐색", exact=True).first.click()
        page.get_by_label("목표 생성물", exact=True).select_option(report["molecule_ids"]["nice-entry3"])
        page.locator(".route-search").get_by_role("button", name="경로 탐색", exact=True).click()
        expect(page.get_by_role("heading", name="연결된 경로가 없습니다")).to_be_visible()
        page.get_by_role("checkbox", name="검토 전 초안 포함", exact=True).check()
        page.locator(".route-search").get_by_role("button", name="경로 탐색", exact=True).click()
        expect(page.locator(".route-card")).to_have_count(1)
        expect(page.locator(".route-card")).to_contain_text("초안 포함")
        mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
        mobile.goto("http://127.0.0.1:8000", wait_until="networkidle")
        mobile.get_by_label("논문 필터", exact=True).select_option("10.1038/nature17431")
        expect(mobile.locator(".reaction-node")).to_have_count(2)
        mobile.locator(".reaction-node").filter(has_text="tert-butyl (6)").click()
        mobile.locator(".evidence-card").filter(has_text="화합물 6").click()
        expect(mobile.get_by_label("원문 페이지", exact=True)).to_have_value("45")
        assert mobile.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        mobile.screenshot(path="/tmp/chembrain-literature-mobile.png", full_page=True)
        assert not errors, errors
        browser.close()
        print(json.dumps({"status": "passed", "checks": ["real records hide demo", "DOI graph filter", "solvent exception", "evidence page 45", "original PDF page anchor", "full-document search", "main/SI links", "bibliographic metadata", "conflicting drafts excluded by default", "explicit draft route", "mobile evidence navigation", "no JS errors"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
