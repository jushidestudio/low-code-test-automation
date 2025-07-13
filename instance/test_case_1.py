import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://www.google.com/")
    page.get_by_role("dialog").locator("div").filter(has_text="Google にログインGoogle").nth(1).click()
    page.get_by_role("combobox", name="検索").click()
    page.get_by_role("combobox", name="検索").fill("anime")