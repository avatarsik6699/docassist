import {
  createPatientViaApi,
  expect,
  loginFirstTimePatientAndSetup,
  loginThroughUi,
  test,
} from './fixtures';

test.describe('phase 04 questionnaire assignment and submission', () => {
  test('doctor assigns PHQ-9 and patient submits it', async ({ page, request, uniqueEmail }) => {
    const createdPatient = await createPatientViaApi(request, uniqueEmail);

    await page.goto('/dashboard');
    await expect(page).toHaveURL(/\/dashboard$/);
    await page.getByTestId('open-patients-link').click();
    await expect(page).toHaveURL(/\/patients$/);

    await page.getByTestId('doctor-medication-patient-select').selectOption(createdPatient.id);
    await page.getByTestId('doctor-questionnaire-code-select').selectOption('PHQ-9');
    await page.getByTestId('assign-questionnaire-submit').click();
    await expect(page.getByTestId('doctor-questionnaire-history')).toContainText('PHQ-9');
    await expect(page.getByTestId('doctor-questionnaire-history')).toContainText('assigned');

    await page.goto('/dashboard');
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await loginFirstTimePatientAndSetup(
      page,
      createdPatient.email,
      createdPatient.temporary_password,
      'permanent123'
    );

    await expect(page.getByTestId('patient-questionnaire-list')).toContainText('PHQ-9');
    await page.getByTestId('open-questionnaire-link').first().click();
    await expect(page).toHaveURL(/\/questionnaires\//);
    await page.getByTestId('question-answer-q1').selectOption('1');
    await page.getByTestId('question-answer-q9').selectOption('1');
    await page.getByTestId('questionnaire-submit').click();
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByTestId('patient-questionnaire-empty')).toBeVisible();

    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await loginThroughUi(page);
    await page.getByTestId('open-patients-link').click();

    await page.getByTestId('doctor-medication-patient-select').selectOption(createdPatient.id);
    await expect(page.getByTestId('doctor-questionnaire-history')).toContainText('completed');
    await expect(page.getByTestId('doctor-questionnaire-history')).toContainText('safety flag');
  });
});
