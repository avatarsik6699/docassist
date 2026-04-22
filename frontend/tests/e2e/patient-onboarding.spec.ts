import { createPatientViaApi, expect, test, unauthenticatedStorageState } from './fixtures';

test.describe('phase 02 patient onboarding', () => {
  test('doctor sees newly created patient account in the roster', async ({
    page,
    request,
    uniqueEmail,
  }) => {
    await createPatientViaApi(request, uniqueEmail);

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard$/);
    await page.getByTestId('open-patients-link').click();
    await expect(page).toHaveURL(/\/patients$/);

    await expect(page.getByTestId('patients-table')).toContainText(uniqueEmail, {
      timeout: 15_000,
    });
  });

  test.describe('patient first login flow', () => {
    test.use({ storageState: unauthenticatedStorageState });

    test('patient is redirected to setup-account after first login', async ({
      page,
      request,
      uniqueEmail,
    }) => {
      const createdPatient = await createPatientViaApi(request, uniqueEmail);

      await page.goto('/login');
      await page.getByTestId('email-input').fill(createdPatient.email);
      await page.getByTestId('password-input').fill(createdPatient.temporary_password);
      await page.getByTestId('login-submit').click();

      await expect(page).toHaveURL(/\/setup-account$/);
      await page.goto('/dashboard');
      await expect(page).toHaveURL(/\/setup-account$/);

      await page.getByTestId('setup-password-input').fill('permanent123');
      await page.getByTestId('setup-password-confirm-input').fill('permanent123');
      await page.getByTestId('setup-account-submit').click();

      await expect(page).toHaveURL(/\/dashboard$/);
      await expect(page.getByTestId('patient-dashboard-card')).toContainText(
        'onboarding is complete'
      );
    });
  });
});
