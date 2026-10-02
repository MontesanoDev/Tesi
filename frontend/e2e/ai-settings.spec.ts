import { expect, test } from '@playwright/test'

test('configure models and persist the project choice across chat and document views', async ({ page, request }, testInfo) => {
  const suffix = `${testInfo.project.name}-${Date.now()}`
  const profileIds: string[] = []
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  const projectResponse = await request.post('/api/projects', { data: {
    title: `Prova modelli ${suffix}`, description: 'Progetto temporaneo del test interfaccia',
  } })
  expect(projectResponse.ok()).toBeTruthy()
  const project = await projectResponse.json()
  // No requests to a real AI provider: only discovery is stubbed in this browser test.
  await page.route('**/api/settings/ai/check', async (route) => {
    const provider = route.request().postDataJSON().provider
    await route.fulfill({ json: { models: [provider === 'ollama' ? 'local-test' : 'remote-test'],
      message: 'Collegamento riuscito. Scegli un modello dall’elenco.' } })
  })
  try {
    await page.goto('/settings')
    await page.getByRole('button', { name: 'Aggiungi modello' }).click()
    await page.getByRole('combobox', { name: 'Servizio', exact: true }).selectOption('deepseek')
    await page.getByLabel('Nome da mostrare').fill(`Cloud ${suffix}`)
    await page.getByLabel('Chiave API', { exact: true }).fill('browser-test-key')
    await page.getByRole('button', { name: 'Verifica collegamento e trova modelli' }).click()
    await expect(page.getByLabel('Modello', { exact: true })).toHaveValue('remote-test')
    const cloudResponse = page.waitForResponse((response) => response.url().endsWith('/settings/ai/profiles') && response.request().method() === 'POST')
    await page.getByRole('button', { name: 'Salva modello' }).click()
    const cloud = await (await cloudResponse).json()
    profileIds.push(cloud.id)
    expect(JSON.stringify(cloud)).not.toContain('browser-test-key')
    await expect(page.getByText(`Cloud ${suffix}`, { exact: true })).toBeVisible()

    await page.getByRole('button', { name: 'Aggiungi modello' }).click()
    await page.getByRole('combobox', { name: 'Servizio', exact: true }).selectOption('ollama')
    await page.getByLabel('Nome da mostrare').fill(`Locale ${suffix}`)
    await expect(page.getByLabel('Chiave API', { exact: true })).toHaveCount(0)
    await page.getByRole('button', { name: 'Verifica collegamento e trova modelli' }).click()
    await expect(page.getByLabel('Modello', { exact: true })).toHaveValue('local-test')
    await page.getByText('Opzioni avanzate', { exact: true }).click()
    await page.getByLabel(/Finestra di contesto/).fill('16384')
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-ai-settings.png`, fullPage: true })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
    const localResponse = page.waitForResponse((response) => response.url().endsWith('/settings/ai/profiles') && response.request().method() === 'POST')
    await page.getByRole('button', { name: 'Salva modello' }).click()
    const local = await (await localResponse).json()
    profileIds.push(local.id)
    expect(local.context_window).toBe(16384)

    await page.goto(`/projects/${project.id}`)
    await expect(page.getByRole('combobox', { name: 'Modello AI' })).toHaveCount(0)
    await page.getByRole('button', { name: 'Impostazioni AI' }).click()
    await page.getByRole('menuitemradio').filter({ hasText: local.name }).click()
    await expect(page.getByRole('status')).toHaveText('Modello aggiornato per questo progetto.')
    await expect(page.getByRole('menu', { name: 'Modello AI' })).toHaveCount(0)
    await page.reload()
    await page.getByRole('button', { name: 'Impostazioni AI' }).click()
    await expect(page.getByRole('menuitemradio').filter({ hasText: local.name })).toHaveAttribute('aria-checked', 'true')
    await expect(page.getByRole('menu', { name: 'Modello AI' })).toBeInViewport()
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-ai-menu.png`, fullPage: true })
    await page.keyboard.press('Escape')
    await expect(page.getByRole('button', { name: 'Impostazioni AI' })).toBeFocused()
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-ai-project.png`, fullPage: true })
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
    await page.goto(`/projects/${project.id}/knowledge?artifact=template`)
    await expect(page.getByLabel('Messaggio per Mapi RAG')).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Moduli e bozze', exact: true })).toHaveCount(0)
    await expect(page.getByRole('combobox', { name: 'Modello AI' })).toHaveCount(0)
    expect((await (await request.get(`/api/projects/${project.id}/ai-model`)).json()).profile_id).toBe(local.id)
    await page.goto(`/projects/${project.id}`)
    await page.getByRole('button', { name: 'Impostazioni AI' }).click()
    await page.getByRole('menuitemradio').filter({ hasText: cloud.name }).click()
    await expect(page.getByRole('status')).toHaveText('Modello aggiornato per questo progetto.')

    await page.goto('/settings')
    const cloudRow = page.locator('.ai-profile-list li').filter({ hasText: `Cloud ${suffix}` })
    await cloudRow.getByRole('button', { name: 'Modifica' }).click()
    await expect(page.getByLabel('Chiave API', { exact: true })).toHaveValue('')
    await page.getByLabel('Nome da mostrare').fill(`Cloud aggiornato ${suffix}`)
    await page.getByRole('button', { name: 'Salva modello' }).click()
    await expect(page.getByText(`Cloud aggiornato ${suffix}`, { exact: true })).toBeVisible()
    const profiles = (await (await request.get('/api/settings/ai')).json()).profiles
    expect(profiles.find((profile: { id: string }) => profile.id === cloud.id).has_api_key).toBe(true)
    expect(JSON.stringify(profiles)).not.toContain('browser-test-key')
    expect(errors).toEqual([])
  } finally {
    await request.delete(`/api/projects/${project.id}`)
    for (const id of profileIds) await request.delete(`/api/settings/ai/profiles/${id}`)
  }
})
