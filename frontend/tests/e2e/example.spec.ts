import { expect, test } from '@playwright/test';

test.describe('phase 01 auth flow', () => {
  test('redirects unauthenticated dashboard visits to login', async ({ page }) => {
    await page.goto('/dashboard');

    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByTestId('login-submit')).toBeVisible();
  });

  test('signs in on the first click and redirects authenticated users away from login', async ({
    page,
  }) => {
    await page.goto('/login');

    await expect(page.getByTestId('login-submit')).toBeEnabled();
    await page.getByTestId('email-input').fill('admin@example.com');
    await page.getByTestId('password-input').fill('changeme123');
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByTestId('dashboard-shell')).toContainText('admin@example.com');
    await expect(page.getByTestId('dashboard-shell')).toContainText('admin');

    await page.goto('/login');
    await expect(page).toHaveURL(/\/dashboard$/);
  });

  test('shows an error for invalid credentials', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByTestId('login-submit')).toBeEnabled();
    await page.getByTestId('email-input').fill('admin@example.com');
    await page.getByTestId('password-input').fill('wrong-password');
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/\/login$/);
    await expect(page.getByTestId('login-error')).toHaveText(
      'Invalid email or password. Please try again.'
    );
  });

  test('logs out and blocks returning to the dashboard', async ({ page }) => {
    await page.goto('/login');

    await expect(page.getByTestId('login-submit')).toBeEnabled();
    await page.getByTestId('email-input').fill('admin@example.com');
    await page.getByTestId('password-input').fill('changeme123');
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/\/dashboard$/);

    await page.getByTestId('logout-button').click();

    await expect(page).toHaveURL(/\/login$/);

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/login$/);
  });
});
