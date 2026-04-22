import { expect, test as base } from '@playwright/test';
import type { APIRequestContext, Page } from '@playwright/test';

export const ADMIN_EMAIL = 'admin@example.com';
export const DOCTOR_EMAIL = 'doctor@example.com';
export const DEFAULT_PASSWORD = 'changeme123';

export type CreatedPatient = {
  id: string;
  email: string;
  temporary_password: string;
};

type TestFixtures = {
  uniqueEmail: string;
};

export const test = base.extend<TestFixtures>({
  uniqueEmail: async ({}, use, testInfo) => {
    const slug = `${testInfo.workerIndex}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
    await use(`e2e-${slug}@example.com`);
  },
});

export const unauthenticatedStorageState = { cookies: [], origins: [] };

export async function waitForAppReady(page: Page): Promise<void> {
  await page.waitForFunction(() => document.documentElement.dataset.appReady === 'true');
}

export async function loginThroughUi(
  page: Page,
  email = DOCTOR_EMAIL,
  password = DEFAULT_PASSWORD
): Promise<void> {
  await page.goto('/login');
  await waitForAppReady(page);
  await expect(page.getByTestId('login-submit')).toBeVisible();
  await page.getByTestId('email-input').fill(email);
  await page.getByTestId('password-input').fill(password);

  const loginResponsePromise = page.waitForResponse(
    (response) =>
      response.url().includes('/api/v1/auth/login') && response.request().method() === 'POST'
  );
  await page.getByTestId('login-submit').click();
  const loginResponse = await loginResponsePromise;

  expect(loginResponse.ok()).toBeTruthy();
  await expect(page).toHaveURL(/\/dashboard$/, { timeout: 15_000 });
}

export async function apiLogin(
  request: APIRequestContext,
  email = DOCTOR_EMAIL,
  password = DEFAULT_PASSWORD
): Promise<string> {
  const response = await request.post('http://localhost:8000/api/v1/auth/login', {
    data: { email, password },
  });
  expect(response.ok()).toBeTruthy();
  const data = await response.json();
  return data.access_token as string;
}

export async function createPatientViaApi(
  request: APIRequestContext,
  patientEmail: string
): Promise<CreatedPatient> {
  const doctorToken = await apiLogin(request);

  const response = await request.post('http://localhost:8000/api/v1/patients', {
    data: { email: patientEmail },
    headers: {
      Authorization: `Bearer ${doctorToken}`,
    },
  });

  expect(response.ok()).toBeTruthy();
  return (await response.json()) as CreatedPatient;
}

export async function loginFirstTimePatientAndSetup(
  page: Page,
  patientEmail: string,
  temporaryPassword: string,
  newPassword = 'permanent123'
): Promise<void> {
  await page.goto('/login');
  await waitForAppReady(page);
  await page.getByTestId('email-input').fill(patientEmail);
  await page.getByTestId('password-input').fill(temporaryPassword);
  await page.getByTestId('login-submit').click();

  await expect(page).toHaveURL(/\/setup-account$/);
  await page.getByTestId('setup-password-input').fill(newPassword);
  await page.getByTestId('setup-password-confirm-input').fill(newPassword);
  await page.getByTestId('setup-account-submit').click();
  await expect(page).toHaveURL(/\/dashboard$/);
}

export { expect };
