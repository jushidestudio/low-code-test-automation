
import { test, expect } from '@playwright/test';

test('Empty placeholder', async ({ page }) => {
  await page.goto('https://example.com');
  expect(page).toBeTruthy();
});
