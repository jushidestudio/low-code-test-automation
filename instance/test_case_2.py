import re
from playwright.sync_api import Page, expect


def test_example(page: Page) -> None:
    page.goto("https://www.yahoo.co.jp/")
    page.get_by_role("searchbox", name="検索したいキーワードを入力してください").click()
    page.get_by_role("searchbox", name="検索したいキーワードを入力してください").fill("rurunn")
    page.get_by_role("searchbox", name="検索したいキーワードを入力してください").press("Enter")
