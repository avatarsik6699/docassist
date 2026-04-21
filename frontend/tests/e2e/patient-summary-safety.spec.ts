import { expect, test } from '@playwright/test';

test.describe('phase 05 patient summary safety highlighting', () => {
  test('doctor sees summary safety flags after patient submissions', async ({ page, request }) => {
    const patientEmail = `phase05-${Date.now()}@example.com`;

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

    await page.getByTestId('doctor-questionnaire-code-select').selectOption('PHQ-9');
    await page.getByTestId('assign-questionnaire-submit').click();

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

    await page.getByTestId('open-questionnaire-link').first().click();
    await expect(page).toHaveURL(/\/questionnaires\//);
    await page.getByTestId('question-answer-q1').selectOption('1');
    await page.getByTestId('question-answer-q9').selectOption('1');
    await page.getByTestId('questionnaire-submit').click();
    await expect(page).toHaveURL(/\/dashboard$/);

    await page.getByTestId('adherence-status-select').selectOption('modified');
    await page.getByTestId('adherence-note-input').fill('Took half dose due to nausea');
    await page.getByTestId('adherence-submit').click();

    await page.getByTestId('side-effect-severity-select').selectOption('severe');
    await page.getByTestId('side-effect-symptom-input').fill('Persistent nausea');
    await page.getByTestId('side-effect-note-input').fill('Worse over 24 hours');
    await page.getByTestId('side-effect-submit').click();
    await expect(page.getByTestId('side-effect-form-success')).toContainText(
      'Side effect reported.'
    );

    await page.goto('/dashboard');
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await page.getByTestId('email-input').fill('doctor@example.com');
    await page.getByTestId('password-input').fill('changeme123');
    await page.getByTestId('login-submit').click();
    await page.getByTestId('open-patients-link').click();

    await page.getByTestId('doctor-medication-patient-select').selectOption(createdPatient.id);
    await expect(page.getByTestId('patient-summary-panel')).toContainText('Recent patient summary');
    await expect(page.getByTestId('patient-summary-safety-flags')).toContainText(
      'Questionnaire safety signal'
    );
    await expect(page.getByTestId('patient-summary-safety-flags')).toContainText(
      'Severe side effect reported'
    );
  });
});
