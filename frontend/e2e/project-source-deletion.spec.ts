import { expect, test } from '@playwright/test'

test('project sources can be removed independently with confirmation', async ({ page }, testInfo) => {
  const files = [
    { id: 21, name: 'avviso-progettazione-sicurezza.pdf', mime_type: 'application/pdf' },
    { id: 22, name: 'nota-operativa.md', mime_type: 'text/markdown' },
  ].map((file) => ({
    ...file, metadata: '1 KB · 2 frammenti', kind: 'source', status: 'Indicizzato',
    page_count: 1, chunk_count: 2,
  }))
  let deleteRequests = 0
  let failNextDeletion = true
  const project = () => ({
    id: 'fonti-test', title: 'Progetto di verifica', description: 'Interventi sulle strutture',
    status: 'In analisi', status_tone: 'info', updated_label: 'ora',
    source_count: files.length, model_count: 0, instructions: '',
    call_fact_count: 0, missing_fact_count: 0, files, conversations: [],
    knowledge_sources: [],
  })
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
    if (path === '/api/projects/fonti-test') {
      await route.fulfill({ json: project() })
    } else if (path.endsWith('/artifacts') || path.endsWith('/document-compilations')) {
      await route.fulfill({ json: [] })
    } else if (route.request().method() === 'DELETE' && /\/files\/\d+$/.test(path)) {
      deleteRequests += 1
      if (failNextDeletion) {
        failNextDeletion = false
        await route.fulfill({ status: 500, json: { detail: 'Eliminazione non riuscita' } })
      } else {
        const index = files.findIndex((file) => file.id === Number(path.split('/').pop()))
        expect(index).toBeGreaterThanOrEqual(0)
        files.splice(index, 1)
        await route.fulfill({ status: 204 })
      }
    } else {
      await route.fulfill({ status: 404, json: { detail: 'Not found' } })
    }
  })

  await page.goto('/projects/fonti-test')
  const panel = page.locator('.project-context-panel')
  await expect(panel.getByText('2 fonti', { exact: true })).toBeVisible()
  const deletePdf = page.getByRole('button', { name: 'Elimina avviso-progettazione-sicurezza.pdf' })
  await deletePdf.scrollIntoViewIfNeeded()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-source-delete-actions.png`, fullPage: true })
  for (const row of await panel.locator('.context-file-row').all()) {
    const rowBox = (await row.boundingBox())!
    const actions = row.locator('.context-file-actions')
    const box = (await actions.boundingBox())!
    expect(box.x + box.width).toBeLessThanOrEqual(rowBox.x + rowBox.width + 1)
    const badgeBox = (await row.locator('.status-pill').boundingBox())!
    expect(badgeBox.x + badgeBox.width).toBeLessThanOrEqual(box.x)
  }
  await deletePdf.click()
  const dialog = page.getByRole('dialog', { name: 'Elimina fonte' })
  await expect(dialog).toBeVisible()
  await expect(dialog.getByRole('button', { name: 'Annulla' })).toBeFocused()
  expect(deleteRequests).toBe(0)
  await page.keyboard.press('Escape')
  await expect(dialog).toHaveCount(0)
  await expect(deletePdf).toBeFocused()

  await deletePdf.click()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-source-delete-confirm.png`, fullPage: true })
  await dialog.getByRole('button', { name: 'Elimina fonte' }).click()
  await expect(dialog.getByRole('alert')).toHaveText('Eliminazione non riuscita')
  await expect(panel.getByText('2 fonti', { exact: true })).toBeVisible()
  await dialog.getByRole('button', { name: 'Elimina fonte' }).click()
  await expect(dialog).toHaveCount(0)
  await expect(panel.getByText('1 fonte', { exact: true })).toBeVisible()
  await expect(deletePdf).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Progetto di verifica' })).toBeVisible()

  const longName = `${'documento'.repeat(18)}.md`
  files[0].name = longName
  await page.reload()
  await page.getByRole('button', { name: `Elimina ${longName}` }).click()
  const dialogSizes = await dialog.evaluate((element) => ({
    width: element.clientWidth, scroll: element.scrollWidth,
  }))
  expect(dialogSizes.scroll).toBeLessThanOrEqual(dialogSizes.width)
  await dialog.getByRole('button', { name: 'Elimina fonte' }).click()
  await expect(panel.getByText('0 fonti', { exact: true })).toBeVisible()
  await expect(panel.getByText('Nessuna fonte nel progetto')).toBeVisible()
  expect(deleteRequests).toBe(3)
  await page.reload()
  await expect(panel.getByText('Nessuna fonte nel progetto')).toBeVisible()
  const sizes = await page.evaluate(() => ({
    width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth,
  }))
  expect(sizes.scroll).toBeLessThanOrEqual(sizes.width)
})
