import { expect, test } from '@playwright/test'

test('projects can switch between modification and name order while filtering', async ({ page }, testInfo) => {
  const projects = [
    { id: 'zeta', title: 'Zeta', description: 'Intervento scuola' },
    { id: 'dieci', title: 'progetto 10', description: 'Rete idrica' },
    { id: 'due', title: 'Progetto 2', description: 'Rete idrica' },
    { id: 'alfa', title: 'Alfa', description: 'Intervento scuola' },
  ].map((item) => ({ ...item, status: 'Bozza', status_tone: 'warning',
    updated_label: 'Aggiornato ora', source_count: 0, model_count: 0,
  }))
  await page.route('**/api/projects', (route) => route.fulfill({ json: projects }))
  await page.goto('/projects')
  const titles = page.locator('.project-card strong')
  const sort = page.getByRole('combobox', { name: 'Ordina progetti' })
  async function search(query: string) {
    await page.locator('.search-control').click()
    await page.getByRole('textbox', { name: 'Cerca progetti' }).fill(query)
  }
  await expect(sort).toHaveValue('updated')
  await expect(titles).toHaveText(['Zeta', 'progetto 10', 'Progetto 2', 'Alfa'])
  await sort.selectOption('name')
  await expect(titles).toHaveText(['Alfa', 'Progetto 2', 'progetto 10', 'Zeta'])
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-projects-sorted-name.png`, fullPage: true })
  await search('scuola')
  await expect(titles).toHaveText(['Alfa', 'Zeta'])
  await sort.selectOption('updated')
  await expect(titles).toHaveText(['Zeta', 'Alfa'])
  await search('nessun risultato')
  await expect(titles).toHaveCount(0)
  await search('')
  await expect(titles).toHaveText(['Zeta', 'progetto 10', 'Progetto 2', 'Alfa'])
  expect(await page.evaluate(() => document.documentElement.scrollWidth
    <= document.documentElement.clientWidth)).toBe(true)
})
