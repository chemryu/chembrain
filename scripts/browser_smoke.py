"""Run with a Python that has playwright installed; uses an isolated temporary DB.

CHROMIUM_PATH can override the system Chromium binary. No browser downloads occur.
"""
import io
import json
import os
import shutil
import subprocess
import tempfile
import time
import urllib.request
import zipfile
from pathlib import Path

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parent.parent


def main():
    with tempfile.TemporaryDirectory(prefix="chembrain-browser-") as tmp:
        log_path = Path(tmp) / "api.log"
        with log_path.open("w") as log:
            process = subprocess.Popen([str(ROOT / ".venv/bin/python"), "-m", "uvicorn", "server.app:app", "--host", "127.0.0.1", "--port", "8765"], cwd=ROOT, env={**os.environ, "CHEMBRAIN_DATA_DIR": str(Path(tmp) / "data")}, stdout=log, stderr=log)
            try:
                for _ in range(60):
                    try:
                        urllib.request.urlopen("http://127.0.0.1:8765/api/health", timeout=1).close()
                        break
                    except OSError:
                        if process.poll() is not None:
                            raise RuntimeError(log_path.read_text())
                        time.sleep(.2)
                else:
                    raise RuntimeError("API did not become ready")
                with sync_playwright() as p:
                    browser = p.chromium.launch(executable_path=os.environ.get("CHROMIUM_PATH") or shutil.which("chromium"), args=["--no-sandbox"])
                    page = browser.new_page(viewport={"width": 1440, "height": 1000}, device_scale_factor=1)
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.goto("http://127.0.0.1:8765", wait_until="networkidle")
                    expect(page.get_by_role("heading", name="아이디어가 반응으로 이어지는 곳")).to_be_visible()
                    expect(page.locator(".molecule-node")).to_have_count(7)
                    expect(page.locator(".reaction-node")).to_have_count(4)
                    page.screenshot(path="/tmp/chembrain-desktop.png", full_page=True)
                    page.get_by_role("button", name="분자 사전", exact=True).click()
                    for name, smiles in [("Methanol fixture", "CO")]:
                        page.get_by_role("button", name="분자 등록", exact=True).click()
                        dialog = page.get_by_role("dialog")
                        dialog.get_by_label("분자 이름", exact=True).fill(name)
                        dialog.locator('input[name="smiles"]').fill(smiles)
                        dialog.get_by_role("button", name="분자 저장", exact=True).click()
                        expect(dialog).not_to_be_visible()
                    page.get_by_role("button", name="자료 보관함", exact=False).click()
                    text = "# Browser smoke fixture only\nMethanol oxidation reaction gives formaldehyde.\nThe isolated yield was 80 percent. Solvent: water."
                    page.locator('input[type="file"]').set_input_files({"name": "browser-fixture.md", "mimeType": "text/markdown", "buffer": text.encode()})
                    expect(page.get_by_role("heading", name="browser-fixture", exact=True)).to_be_visible()
                    expect(page.locator(".source-text")).to_contain_text("80 percent")
                    page.get_by_role("button", name="이 페이지로 반응 기록").click()
                    dialog = page.get_by_role("dialog")
                    dialog.locator('input[name="name"]').fill("Browser fixture oxidation")
                    dialog.get_by_role("button", name="새 분자 등록", exact=True).click()
                    nested = page.get_by_role("dialog", name="분자 등록", exact=True)
                    nested.get_by_label("분자 이름", exact=True).fill("Formaldehyde fixture")
                    nested.locator('input[name="smiles"]').fill("C=O")
                    nested.get_by_role("button", name="분자 저장", exact=True).click()
                    expect(nested).not_to_be_visible()
                    dialog = page.get_by_role("dialog", name="새로운 반응 기록", exact=True)
                    expect(dialog.locator('input[name="name"]')).to_have_value("Browser fixture oxidation")
                    dialog.get_by_label("방법론", exact=True).select_option("photochemical")
                    dialog.get_by_label("반응물 추가", exact=True).select_option(label="Methanol fixture")
                    dialog.get_by_label("생성물 추가", exact=True).select_option(label="Formaldehyde fixture")
                    dialog.get_by_label("파장", exact=True).fill("450 nm")
                    dialog.get_by_label("수율 (%)", exact=True).fill("80")
                    dialog.get_by_label("검토 상태", exact=True).select_option("reviewed")
                    dialog.get_by_role("button", name="반응 저장", exact=True).click()
                    expect(dialog).not_to_be_visible()
                    expect(page.locator(".inspector h2")).to_have_text("Browser fixture oxidation")
                    expect(page.locator(".conditions")).to_contain_text("450 nm")
                    expect(page.locator(".inspector .badge.reviewed")).to_be_visible()
                    page.get_by_role("button", name="경로 탐색", exact=True).first.click()
                    page.get_by_label("목표 생성물", exact=True).select_option(label="Formaldehyde fixture")
                    page.locator(".route-search").get_by_role("button", name="경로 탐색", exact=True).click()
                    expect(page.locator(".route-card")).to_have_count(1)
                    expect(page.locator(".route-card")).to_contain_text("Methanol fixture")
                    expect(page.locator(".availability-warning")).to_contain_text("미확인 1종")
                    with page.expect_download() as download_info:
                        page.get_by_role("link", name="Markdown 내보내기").click()
                    downloaded = Path(download_info.value.path()).read_bytes()
                    with zipfile.ZipFile(io.BytesIO(downloaded)) as archive:
                        assert any("Browser fixture oxidation" in archive.read(name).decode() for name in archive.namelist() if name.endswith(".md"))
                    page.get_by_role("button", name="반응 지도", exact=True).click()
                    page.get_by_placeholder("분자, 반응, SMILES 검색").fill("not-a-real-molecule")
                    expect(page.get_by_role("heading", name="검색 결과가 없습니다")).to_be_visible()
                    page.get_by_role("button", name="검색 초기화", exact=True).click()
                    expect(page.locator(".molecule-node")).to_have_count(9)
                    page.reload(wait_until="networkidle")
                    expect(page.locator(".molecule-node")).to_have_count(2)
                    expect(page.get_by_role("checkbox", name="데모 포함")).not_to_be_checked()
                    mobile = browser.new_page(viewport={"width": 390, "height": 844}, device_scale_factor=1, is_mobile=True, has_touch=True)
                    mobile.goto("http://127.0.0.1:8765", wait_until="networkidle")
                    expect(mobile.locator(".molecule-node")).to_have_count(2)
                    assert mobile.evaluate("document.documentElement.scrollWidth <= window.innerWidth"), "Mobile page overflows"
                    mobile.screenshot(path="/tmp/chembrain-mobile.png", full_page=True)
                    assert not errors, errors
                    browser.close()
                    print(json.dumps({"status": "passed", "checks": ["desktop graph", "molecule creation", "upload and text extraction", "evidence-backed reaction", "photochemical condition", "route and availability", "Markdown export", "search empty state", "persistent reload", "mobile layout", "no JS errors"], "screenshots": ["/tmp/chembrain-desktop.png", "/tmp/chembrain-mobile.png"]}, ensure_ascii=False))
            finally:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


if __name__ == "__main__":
    main()
