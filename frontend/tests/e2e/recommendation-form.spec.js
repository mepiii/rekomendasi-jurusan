// Purpose: Smoke test Apti option-first recommendation form.
// Callers: Playwright test runner.
// Deps: Frontend dev server and Chrome stable.
// API: Verifies predefined option chips drive the prodi intake flow.
// Side effects: Opens browser page and clicks form controls.
import { expect, test } from '@playwright/test';

test('prodi intake exposes predefined selectable options', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: /skip for now|lewati/i }).click();
  await expect(page.getByText(/Apti advisory workspace|ruang rekomendasi apti/i)).toBeVisible();

  await page.getByRole('button', { name: /continue|lanjut/i }).click();
  await expect(page.getByLabel(/Pendidikan Agama/i)).toBeVisible();

  for (const label of ['Pendidikan Agama', 'PPKn', 'Bahasa Indonesia', 'Bahasa Inggris', 'Matematika Umum', 'PJOK', 'Seni', 'Biologi', 'Fisika', 'Kimia', 'Matematika Peminatan']) {
    const input = page.getByLabel(new RegExp(label, 'i'));
    if (await input.count()) await input.fill('88');
  }

  for (const name of ['Technology', 'Engineering', 'Data / AI', 'Numbers', 'Technical', 'Independent']) {
    await page.getByRole('button', { name }).click();
  }

  await page.getByRole('button', { name: /continue|lanjut/i }).click();
  await expect(page.getByRole('button', { name: 'STEM-heavy classes' })).toBeVisible();
  await page.getByRole('button', { name: 'STEM-heavy classes' }).click();
  await expect(page.getByLabel('Academic context')).toHaveValue('STEM-heavy classes');
});
