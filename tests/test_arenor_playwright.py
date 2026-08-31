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
SEVEN_RESULTS = ["zzz", "10", "130", "140", "150", "155", "160"]


def set_results(page, selector_prefix, values):
    for index, value in enumerate(values):
        page.locator(f"#{selector_prefix}-{index}").select_option(value)


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
        assert page.locator("h2").filter(has_text="2. 各試合の戦績/PT表示設定").count() == 1
        assert page.locator('input[name="selfPartyVisibility"][value="show"]').is_checked()
        assert not page.locator('input[name="selfPartyVisibility"][value="hide"]').is_checked()
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
        assert page.locator(".secret-checkbox").count() == 7
        assert page.locator(".secret-checkbox").evaluate_all(
            "checkboxes => checkboxes.every(checkbox => !checkbox.checked && !checkbox.disabled)"
        )
        assert page.locator("#points-0 option").first.inner_text() == "zzz"
        assert page.locator("#points-0 option").first.get_attribute("value") == "zzz"
        assert page.locator("#defenseStat-0 option").first.inner_text() == "zzz"
        assert page.locator("#defenseStat-0 option").first.get_attribute("value") == "zzz"
        page.locator("#points-0").select_option("zzz")
        assert page.locator("#secret-0").is_checked()
        assert page.locator("#secret-0").is_disabled()
        page.locator("#points-0").select_option("130")
        assert not page.locator("#secret-0").is_checked()
        assert page.locator("#secret-0").is_enabled()
        set_results(page, "points", SEVEN_RESULTS)
        set_results(page, "defenseStat", SEVEN_RESULTS)
        page.locator("#secret-2").check()
        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")

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
        self_row_non_white_pixels = canvas.evaluate(
            """canvas => {
                const ctx = canvas.getContext('2d');
                const canvasPadding = 25;
                const gap = 15;
                const matchWidth = Math.max(150, Math.floor(canvas.width * 0.2));
                const pointsWidth = Math.floor(canvas.width * 0.15);
                const stripWidth = Math.floor(
                    (canvas.width - canvasPadding * 2 - matchWidth - gap * 2 - pointsWidth) / 2
                );
                const selfX = canvasPadding + matchWidth + gap + stripWidth + gap;
                const rowStart = 50 + Math.max(16, Math.floor(20 * (canvas.width / 750))) + 30;
                const sourceWidth = 1179 * (1 - 2 * 0.11);
                const sourceHeight = 2556 * 0.10;
                const rowHeight = stripWidth * (sourceHeight / sourceWidth);
                const counts = [];
                for (let row = 0; row < 3; row++) {
                    const y = Math.floor(rowStart + row * (rowHeight + 15));
                    const data = ctx.getImageData(
                        Math.floor(selfX), y, Math.floor(stripWidth), Math.floor(rowHeight)
                    ).data;
                    let count = 0;
                    for (let index = 0; index < data.length; index += 4) {
                        if (data[index] < 250 || data[index + 1] < 250 || data[index + 2] < 250) count++;
                    }
                    counts.push(count);
                }
                return counts;
            }"""
        )
        assert self_row_non_white_pixels[0] > 100
        assert self_row_non_white_pixels[0] < self_row_non_white_pixels[1] / 5
        assert self_row_non_white_pixels[2] > 100
        assert self_row_non_white_pixels[2] < self_row_non_white_pixels[1] / 5
        assert not page_errors, page_errors

        data_url = canvas.evaluate("canvas => canvas.toDataURL('image/png')")
        output = base64.b64decode(data_url.split(",", 1)[1])
        (ARTIFACT_DIR / "arenor_with_defense.png").write_bytes(output)
        page.screenshot(path=str(ARTIFACT_DIR / "arenor_iphone16.png"), full_page=True)

        (ARTIFACT_DIR / "arenor_with_defense_zzz.png").write_bytes(output)

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
        set_results(page, "points", SEVEN_RESULTS[:3])
        page.locator("#secret-2").check()
        page.locator("#generateButton").click()
        page.wait_for_function(
            "document.querySelector('#downloadLink').style.display === 'block'",
            timeout=30_000,
        )
        assert page.locator(".row-setting").count() == 3
        assert page.locator(".defense-stat-select").count() == 3
        assert canvas.evaluate("canvas => canvas.height") > 0
        visible_three_size = canvas.evaluate(
            "canvas => ({width: canvas.width, height: canvas.height})"
        )

        page.locator('input[name="selfPartyVisibility"][value="hide"]').check()
        page.locator("#generateButton").click()
        page.wait_for_function(
            "document.querySelector('#downloadLink').style.display === 'block'",
            timeout=30_000,
        )
        hidden_size = canvas.evaluate(
            "canvas => ({width: canvas.width, height: canvas.height})"
        )
        match_width = max(150, int(visible_three_size["width"] * 0.2))
        points_width = int(visible_three_size["width"] * 0.15)
        strip_width = int(
            (visible_three_size["width"] - 25 * 2 - match_width - 15 * 2 - points_width) / 2
        )
        assert hidden_size["width"] == visible_three_size["width"] - strip_width - 15
        assert hidden_size["height"] == visible_three_size["height"]
        hidden_data_url = canvas.evaluate("canvas => canvas.toDataURL('image/png')")
        hidden_output = base64.b64decode(hidden_data_url.split(",", 1)[1])
        (ARTIFACT_DIR / "arenor_self_party_hidden.png").write_bytes(hidden_output)
        assert not page_errors, page_errors
        browser.close()


if __name__ == "__main__":
    main()
