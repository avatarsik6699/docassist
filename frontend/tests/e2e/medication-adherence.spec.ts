import { expect, test } from '@playwright/test';

test.describe('phase 03 medication adherence', () => {
  test('doctor assigns medication and sees patient adherence history', async ({
    page,
    request,
  }) => {
    const patientEmail = `meds-${Date.now()}@example.com`;

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
    await page.getByTestId('email-input').fill('doctor@example.com');
    await page.getByTestId('password-input').fill('changeme123');
    await page.getByTestId('login-submit').click();

    await expect(page).toHaveURL(/\/dashboard$/);
    await page.getByTestId('open-patients-link').click();
    await expect(page).toHaveURL(/\/patients$/);

    await page.getByTestId('doctor-medication-patient-select').selectOption(createdPatient.id);
    await page.getByTestId('medication-name-input').fill('Sertraline');
    await page.getByTestId('medication-dosage-input').fill('50 mg once daily');
    await page.getByTestId('create-medication-submit').click();

    await expect(page.getByTestId('patient-medication-list')).toContainText('Sertraline');

    await page.goto('/dashboard');
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await page.getByTestId('email-input').fill(patientEmail);
    await page.getByTestId('password-input').fill(createdPatient.temporary_password);
    await page.getByTestId('login-submit').click();
    await expect(page).toHaveURL(/\/setup-account$/);

    await page.getByTestId('setup-password-input').fill('permanent123');
    await page.getByTestId('setup-password-confirm-input').fill('permanent123');
    await page.getByTestId('setup-account-submit').click();
    await expect(page).toHaveURL(/\/dashboard$/);

    await expect(page.getByTestId('patient-medication-list')).toContainText('Sertraline');
    await page.getByTestId('adherence-status-select').selectOption('modified');
    await page.getByTestId('adherence-note-input').fill('Took half dose after nausea');
    await page.getByTestId('adherence-submit').click();
    await expect(page.getByTestId('adherence-form-success')).toContainText('Adherence saved.');

    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await page.getByTestId('email-input').fill('doctor@example.com');
    await page.getByTestId('password-input').fill('changeme123');
    await page.getByTestId('login-submit').click();
    await expect(page).toHaveURL(/\/dashboard$/);
    await page.getByTestId('open-patients-link').click();

    await page.getByTestId('doctor-medication-patient-select').selectOption(createdPatient.id);
    await expect(page.getByTestId('doctor-adherence-history')).toContainText('modified');
    await expect(page.getByTestId('doctor-adherence-history')).toContainText(
      'Took half dose after nausea'
    );
  });
});
