import { expect, test } from '@playwright/test';

test.describe('phase 02 patient onboarding', () => {
  test('doctor creates a patient account from the roster', async ({ page }) => {
    const patientEmail = `playwright-${Date.now()}@example.com`;

    await page.goto('/login');

    await page.getByTestId('email-input').fill('doctor@example.com');
    await page.getByTestId('password-input').fill('changeme123');
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await page.getByTestId('open-patients-link').click();

    await expect(page).toHaveURL(/\/patients$/);
    await page.getByTestId('patient-email-input').fill(patientEmail);
    await page.getByTestId('create-patient-submit').click();

    await expect(page.getByTestId('temporary-password-card')).toBeVisible();
    await expect(page.getByTestId('temporary-password-value')).not.toHaveText('');
    await expect(page.getByTestId('patients-table')).toContainText(patientEmail);
  });

  test('patient is redirected to setup-account after first login', async ({ page, request }) => {
    const patientEmail = `pw-${Date.now()}@example.com`;

    const doctorLoginResponse = await request.post('http://localhost:8000/api/v1/auth/login', {
      data: {
        email: 'doctor@example.com',
        password: 'changeme123',
      },
    });
    expect(doctorLoginResponse.ok()).toBeTruthy();
    const doctorLogin = await doctorLoginResponse.json();

    const createPatientResponse = await request.post('http://localhost:8000/api/v1/patients', {
      data: {
        email: patientEmail,
      },
      headers: {
        Authorization: `Bearer ${doctorLogin.access_token}`,
      },
    });
    expect(createPatientResponse.ok()).toBeTruthy();
    const createdPatient = await createPatientResponse.json();

    await page.goto('/login');
    await page.getByTestId('email-input').fill(patientEmail);
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
