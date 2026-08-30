import base64
import os
from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:8000/arenor.html"
CHALLENGE_IMAGE = Path(
    os.environ.get("ARENOR_CHALLENGE_IMAGE", Path.home() / "Downloads" / "IMG_4845.PNG")
)
DEFENSE_IMAGE = Path(
    os.environ.get("ARENOR_DEFENSE_IMAGE", Path.home() / "Downloads" / "IMG_4864.PNG")
)
ARTIFACT_DIR = Path(".tools/playwright/artifacts")


def main():
    assert CHALLENGE_IMAGE.exists(), f"挑戦画像が見つかりません: {CHALLENGE_IMAGE}"
    assert DEFENSE_IMAGE.exists(), f"防衛画像が見つかりません: {DEFENSE_IMAGE}"
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(
            viewport={"width": 393, "height": 852},
            device_scale_factor=3,
            is_mobile=True,
            has_touch=True,
        )
        page_errors = []
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.goto(BASE_URL, wait_until="domcontentloaded", timeout=15_000)

        defense_options = page.locator("#defenseOptions")
        assert not defense_options.evaluate("element => element.open")
        assert defense_options.locator("summary").inner_text() == "ギルド大会用の防衛パーティを追加"
        defense_options.locator("summary").click()
        assert defense_options.evaluate("element => element.open")
        assert page.locator(".defense-stat-select").count() == 0
        assert page.locator("#defenseCommentInput").count() == 0
        assert page.locator("#cropSx").count() == 0
        assert page.locator("#defenseCropX").count() == 0
        assert page.locator("#defenseCropWidth").count() == 0
        assert page.locator("#cropSOpponentY").input_value() == "36"
        assert page.locator("#defenseCropY").input_value() == "40"
        assert page.locator("#defenseCropHeight").input_value() == "16"
        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")

        image_paths = [str(CHALLENGE_IMAGE)] * 7
        page.locator("#imageUpload").set_input_files(image_paths)
        page.locator("#defenseImageUpload").set_input_files(str(DEFENSE_IMAGE))
        page.locator("#commentInput").fill("末尾のひとことを残します")

        page.locator("#generateButton").wait_for(state="visible")
        page.wait_for_function("!document.querySelector('#generateButton').disabled")
        page.wait_for_function("document.querySelector('#defenseFileStatus').textContent.includes('1179 × 2556')")
        assert page.locator(".row-setting").count() == 7
        assert page.locator("#rowsContainer select").evaluate_all(
            "selects => selects.every(select => select.value === '160')"
        )
        defense_results = ["0", "10", "130", "140", "150", "155", "160"]
        for index, value in enumerate(defense_results):
            page.locator(f"#defenseStat-{index}").select_option(value)

        page.locator("#generateButton").click()
        page.wait_for_function(
            "document.querySelector('#downloadLink').style.display === 'block'",
            timeout=30_000,
        )

        canvas = page.locator("#resultCanvas")
        canvas_size = canvas.evaluate("canvas => ({width: canvas.width, height: canvas.height})")
        assert canvas_size["width"] == 2122
        assert canvas_size["height"] > 1700
        assert page.locator("#downloadLink").get_attribute("download").startswith(
            "DQTACT_BattleLogSummary_"
        )

        red_pixels = canvas.evaluate(
            """canvas => {
                const data = canvas.getContext('2d').getImageData(0, 0, canvas.width, canvas.height).data;
                let count = 0;
                for (let index = 0; index < data.length; index += 4) {
                    if (data[index] > 180 && data[index + 1] < 80 && data[index + 2] < 80) count++;
                }
                return count;
            }"""
        )
        assert red_pixels > 100
        assert not page_errors, page_errors

        data_url = canvas.evaluate("canvas => canvas.toDataURL('image/png')")
        output = base64.b64decode(data_url.split(",", 1)[1])
        (ARTIFACT_DIR / "arenor_with_defense.png").write_bytes(output)
        page.screenshot(path=str(ARTIFACT_DIR / "arenor_iphone16.png"), full_page=True)

        page.locator("#clearDefenseImageButton").click()
        assert page.locator("#defenseFileStatus").inner_text() == "画像は選択されていません。"
        assert canvas.evaluate("canvas => canvas.height") == 0

        page.locator("#generateButton").click()
        page.wait_for_function(
            "document.querySelector('#downloadLink').style.display === 'block'",
            timeout=30_000,
        )
        without_defense_size = canvas.evaluate(
            "canvas => ({width: canvas.width, height: canvas.height})"
        )
        assert without_defense_size["width"] == canvas_size["width"]
        assert without_defense_size["height"] < canvas_size["height"]
        without_defense_data_url = canvas.evaluate("canvas => canvas.toDataURL('image/png')")
        without_defense_output = base64.b64decode(without_defense_data_url.split(",", 1)[1])
        (ARTIFACT_DIR / "arenor_without_defense.png").write_bytes(without_defense_output)

        page.locator("#imageUpload").set_input_files([str(CHALLENGE_IMAGE)] * 3)
        page.wait_for_function("!document.querySelector('#generateButton').disabled")
        page.locator("#generateButton").click()
        page.wait_for_function(
            "document.querySelector('#downloadLink').style.display === 'block'",
            timeout=30_000,
        )
        assert page.locator(".row-setting").count() == 3
        assert page.locator(".defense-stat-select").count() == 3
        assert canvas.evaluate("canvas => canvas.height") > 0
        assert not page_errors, page_errors
        browser.close()


if __name__ == "__main__":
    main()
