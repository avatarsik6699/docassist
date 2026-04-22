import {
  createPatientViaApi,
  expect,
  loginFirstTimePatientAndSetup,
  loginThroughUi,
  test,
} from './fixtures';

test.describe('phase 03 medication adherence', () => {
  test('doctor assigns medication and sees patient adherence history', async ({
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

    await expect(page.getByTestId('patient-medication-list')).toContainText('Sertraline');

    await page.goto('/dashboard');
    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await loginFirstTimePatientAndSetup(
      page,
      createdPatient.email,
      createdPatient.temporary_password,
      'permanent123'
    );

    await expect(page.getByTestId('patient-medication-list')).toContainText('Sertraline');
    await page.getByTestId('adherence-status-select').selectOption('modified');
    await page.getByTestId('adherence-note-input').fill('Took half dose after nausea');
    await page.getByTestId('adherence-submit').click();
    await expect(page.getByTestId('adherence-form-success')).toContainText('Adherence saved.');

    await page.getByTestId('logout-button').click();
    await expect(page).toHaveURL(/\/login$/);

    await loginThroughUi(page);
    await page.getByTestId('open-patients-link').click();

    await page.getByTestId('doctor-medication-patient-select').selectOption(createdPatient.id);
    await expect(page.getByTestId('doctor-adherence-history')).toContainText('modified');
    await expect(page.getByTestId('doctor-adherence-history')).toContainText(
      'Took half dose after nausea'
    );
  });
});
