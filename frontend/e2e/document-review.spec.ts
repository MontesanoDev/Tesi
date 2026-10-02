import { expect, test } from '@playwright/test'

test.beforeEach(async ({ page }) => {
  await page.route('**/api/**', async (route) => {
    const pathname = new URL(route.request().url()).pathname
    if (pathname === '/api/projects/review-test') {
      await route.fulfill({ json: {
        id: 'review-test', title: 'Progetto test', description: '', status: 'In analisi',
        status_tone: 'info', updated_label: '', source_count: 0, model_count: 0,
        instructions: '', call_fact_count: 0, missing_fact_count: 0,
        files: [], knowledge_sources: [], conversations: [],
      } })
    } else if (pathname === '/api/projects/review-test/document-review') {
      await route.fulfill({ json: {
        title: 'Documento test', subtitle: '', completed_fields: 0, total_fields: 0, fields: [],
      } })
    } else {
      await route.fulfill({ status: 404, json: { detail: 'Risorsa di test non prevista' } })
    }
  })
})

test('document review shows API errors instead of a permanent spinner', async ({ page }, testInfo) => {
  await page.route('**/api/projects/review-test/document-review', async (route) => {
    await route.fulfill({ status: 503, json: { detail: 'Revisione non disponibile' } })
  })

  await page.goto('/projects/review-test/review')
  await expect(page.getByRole('alert')).toHaveText('Revisione non disponibile')
  await expect(page.getByRole('status')).toHaveCount(0)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-review-error.png` })
})

test('document review shows project errors even without review data', async ({ page }) => {
  await page.route('**/api/projects/review-test', async (route) => {
    await route.fulfill({ status: 404, json: { detail: 'Progetto non trovato' } })
  })
  await page.route('**/api/projects/review-test/document-review', async (route) => {
    await route.fulfill({ status: 404, json: { detail: 'Documento non trovato' } })
  })

  await page.goto('/projects/review-test/review')
  await expect(page.getByRole('alert')).toHaveText('Progetto non trovato')
  await expect(page.getByRole('status')).toHaveCount(0)
})

test('document review handles an empty document without NaN progress', async ({ page }, testInfo) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  await page.goto('/projects/review-test/review')

  await expect(page.getByRole('heading', { name: 'Documento test' })).toBeVisible()
  await expect(page.getByText('0% completato')).toBeVisible()
  await expect(page.locator('.progress-track > span')).toHaveAttribute('style', 'width: 0%;')
  await expect(page.getByText(/NaN/)).toHaveCount(0)
  await expect(page.getByText('Demo', { exact: true })).toBeVisible()
  await expect(page.getByRole('link', { name: 'Apri chat del progetto' })).toHaveAttribute('href', '/projects/review-test')
  await expect(page.getByRole('button', { name: 'Salva', exact: true })).toHaveCount(0)
  expect(errors).toEqual([])
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-review-empty.png`, fullPage: true })
})
