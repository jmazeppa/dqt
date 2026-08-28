from pathlib import Path

from playwright.sync_api import sync_playwright


BASE_URL = "http://127.0.0.1:8000/self_calc.html"
ARTIFACT_DIR = Path(".tools/playwright/artifacts")


def row_values(page, stat, stage=None):
    for row in page.locator("#resultBody tr").all():
        label = row.locator("th").inner_text()
        if stat in label and (stage is None or stage in label):
            return [cell.inner_text() for cell in row.locator("td").all()]
    raise AssertionError(f"結果行が見つかりません: {stat} {stage or ''}")


def main():
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
        page.wait_for_timeout(1_000)

        assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth")

        # A: デフォルト5凸と0～5凸計算
        assert page.locator("#awakeningArea").is_visible()
        assert page.locator("#awakeningLevel").input_value() == "5"
        page.locator("#baseATK").fill("100")
        assert row_values(page, "攻撃") == ["125", "140", "155", "170"]
        page.locator("#awakeningLevel").select_option("3")
        assert row_values(page, "攻撃") == ["115", "130", "145", "160"]

        # B: 完凸図鑑値を切り上げで逆算し、固定値・MR・覚醒を適用
        page.locator('input[name="calcMode"][value="theory"]').check()
        assert page.locator("#awakeningArea").is_hidden()
        page.locator("#baseATK").fill("")
        page.locator("#baseDEF").fill("")
        page.locator("#fixedAGL").fill("182")
        page.locator("#mrLevel").fill("63")

        # 出典と選定条件: knowledge/status.md「開幕ランキングを使った回帰テストの作成手順」
        # 外部サイトへ依存せず、確認済み掲載値を固定して計算ロジックを回帰検証する。
        theory_cases = [
            ("アマテア", "557", "854"),
            ("魔剣士ピサロ", "645", "949"),
            ("ゲルダ", "637", "941"),
            ("サンタアリーナ", "636", "939"),
        ]
        for character_name, encyclopedia_value, expected in theory_cases:
            page.locator("#characterName").fill(character_name)
            page.locator("#baseAGL").fill(encyclopedia_value)
            assert row_values(page, "素早")[0] == expected

        page.locator("#baseAGL").fill("557")
        page.locator("#resultBody tr").filter(has_text="素早").locator("td").first.click()
        formula = page.locator("#formulaDisplay").inner_text()
        assert "ceil(557 [完凸図鑑値] ÷ 1.25) → 446" in formula

        # C: 覚醒選択を再表示し、MR9～12列とゾーマ実測値を検証
        page.locator('input[name="calcMode"][value="battle"]').check()
        assert page.locator("#awakeningArea").is_visible()
        page.locator("#awakeningLevel").select_option("5")
        headers = [header.inner_text() for header in page.locator("thead th").all()]
        assert headers == ["ステ/段階", "MR9%", "MR10%", "MR11%", "MR12%"]

        page.locator("#baseATK").fill("")
        page.locator("#baseDEF").fill("")
        page.locator("#baseAGL").fill("781")
        page.locator("#battleStageAGL").select_option("0")
        page.locator("#conditionRate").fill("-10")
        assert row_values(page, "素早", "1up") == ["839", "839", "≈838", "≈838"]

        agl_one_up_row = page.locator("#resultBody tr").filter(has_text="素早").filter(has_text="1up")
        agl_one_up_row.locator("td").nth(1).click()
        formula = page.locator("#formulaDisplay").inner_text()
        assert "MR10%" in formula
        assert "A = 579" in formula
        assert "= 839" in formula
        assert not page_errors, page_errors

        page.screenshot(path=str(ARTIFACT_DIR / "self_calc_iphone16.png"), full_page=True)
        browser.close()


if __name__ == "__main__":
    main()
