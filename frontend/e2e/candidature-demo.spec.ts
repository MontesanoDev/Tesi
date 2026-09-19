import { expect, test } from '@playwright/test'

async function expectNoOverflow(page: import('@playwright/test').Page) {
  const dimensions = await page.evaluate(() => ({ width: document.documentElement.clientWidth, content: document.documentElement.scrollWidth }))
  expect(dimensions.content).toBeLessThanOrEqual(dimensions.width)
}

test('conceptual candidature flow is isolated and exports an honest facsimile', async ({ page }, testInfo) => {
  const apiRequests: string[] = []
  page.on('request', (request) => { if (new URL(request.url()).pathname.startsWith('/api/')) apiRequests.push(request.url()) })
  await page.goto('/demo/candidatura')
  await expect(page.getByText('Demo concettuale')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Simula compilazione' })).toBeDisabled()
  await expectNoOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-demo-model.png`, fullPage: true })

  await page.getByRole('button', { name: 'Usa modello dimostrativo' }).click()
  await page.getByRole('button', { name: 'Simula compilazione' }).click()
  await expect(page.locator('.demo-paper')).toContainText('Comune di Valleverde')
  await page.getByRole('button', { name: 'Revisiona bozza' }).click()
  await expect(page.getByRole('button', { name: "Vai all'esportazione" })).toBeDisabled()
  await page.getByLabel('Responsabile del procedimento').fill('Referente della demo')
  await page.getByLabel('Importo richiesto (EUR)').fill('450000')
  await page.getByLabel('Ho controllato i dati del facsimile').check()
  await expectNoOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-demo-review.png`, fullPage: true })
  await page.getByRole('button', { name: "Vai all'esportazione" }).click()

  const downloadPromise = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Scarica facsimile HTML' }).click()
  const download = await downloadPromise
  expect(download.suggestedFilename()).toBe('facsimile-candidatura-demo.html')
  await download.saveAs(testInfo.outputPath('facsimile-candidatura-demo.html'))
  await expect(page.getByRole('status')).toHaveText('Download del facsimile avviato.')
  await expectNoOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-demo-export.png`, fullPage: true })

  await page.evaluate(() => {
    window.print = () => { document.documentElement.dataset.printRequested = 'true' }
  })
  await page.getByRole('button', { name: 'Stampa / PDF' }).click()
  await expect(page.locator('html')).toHaveAttribute('data-print-requested', 'true')
  await page.emulateMedia({ media: 'print' })
  await expect(page.locator('.demo-controls')).toBeHidden()
  await expect(page.getByRole('complementary', { name: 'Navigazione principale' })).toBeHidden()
  await expect(page.locator('.demo-paper')).toBeVisible()
  await expect(page.locator('.demo-paper')).toContainText('Referente della demo')
  await page.pdf({ path: testInfo.outputPath('facsimile-candidatura-demo.pdf'), preferCSSPageSize: true })
  expect(apiRequests).toEqual([])
})

test('uploaded filenames cannot overflow and are not presented as parsed documents', async ({ page }, testInfo) => {
  await page.goto('/demo/candidatura')
  const name = `${'modello-candidatura-'.repeat(12)}.pdf`
  await page.getByLabel('Seleziona modello dimostrativo').setInputFiles({ name, mimeType: 'application/pdf', buffer: Buffer.from('file dimostrativo non elaborato') })
  await expect(page.getByText(name)).toBeVisible()
  await expect(page.getByText(/Il file non viene letto o conservato/)).toBeVisible()
  await expectNoOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-demo-upload.png`, fullPage: true })
})
