import {
  createPatientViaApi,
  expect,
  loginFirstTimePatientAndSetup,
  loginThroughUi,
  test,
} from './fixtures';

test.describe('phase 05 patient summary safety highlighting', () => {
  test('doctor sees summary safety flags after patient submissions', async ({
    page,
    request,
    uniqueEmail,
  }) => {
    const createdPatient = await createPatientViaApi(request, uniqueEmail);

    await page.goto('/dashboard');
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

    await loginFirstTimePatientAndSetup(
      page,
      createdPatient.email,
      createdPatient.temporary_password,
      'permanent123'
    );

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

    await loginThroughUi(page);
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
