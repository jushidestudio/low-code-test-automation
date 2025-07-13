import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.yahoo.co.jp/")
    page.get_by_role("searchbox", name="検索したいキーワードを入力してください").click()
    page.get_by_role("searchbox", name="検索したいキーワードを入力してください").click()
    page.get_by_role("link", name="スポーツ", exact=True).click()
    page.get_by_role("link", name="国内").click()
    page.get_by_role("link", name="プレミアムへ遷移する", exact=True).click()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
