import { expect, test } from '@playwright/test'

test('the composer gear selects models without taking space above the chat', async ({ page }, testInfo) => {
  const profiles = [
    { id: 'cloud', name: 'DeepSeek', provider: 'deepseek', model: 'deepseek-v4-flash',
      base_url: 'https://provider.test', context_window: 32768, has_api_key: true },
    { id: 'local', name: 'Ollama locale', provider: 'ollama', model: 'modello-locale',
      base_url: 'http://127.0.0.1:11434', context_window: 32768, has_api_key: false },
  ]
  let selected: string | null = null
  let answers = 0
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles, default_profile_id: 'cloud' } })
    if (path.endsWith('/ai-model')) {
      if (route.request().method() === 'PUT') selected = route.request().postDataJSON().profile_id
      return route.fulfill({ json: { profile_id: selected, effective_profile: profiles.find((profile) => profile.id === (selected ?? 'cloud')) } })
    }
    if (path === '/api/projects/menu-ui') return route.fulfill({ json: {
      id: 'menu-ui', title: 'Catanzaro — Direzione lavori', description: 'Preparazione della candidatura',
      status: 'In analisi', status_tone: 'info', updated_label: '', source_count: 0, model_count: 0,
      instructions: '', call_fact_count: 0, missing_fact_count: 0, files: [], knowledge_sources: [], conversations: [],
    } })
    if (path.endsWith('/answer')) {
      answers += 1
      return route.fulfill({ json: { conversation_id: 'conversation-ui', turn_id: 1,
        question: 'Quali dati mancano?', answer: 'Aggiungi le fonti del progetto per iniziare.',
        generation_status: 'completed', model: 'modello-locale', evidence: [], citations: [],
        missing_information: [], notice: null, total_tokens: 0,
      } })
    }
    return route.fulfill({ json: [] })
  })
  await page.goto('/projects/menu-ui')
  const gear = page.getByRole('button', { name: 'Impostazioni AI' })
  await expect(gear).toBeVisible()
  await expect(page.locator('.composer').getByRole('button', { name: 'Impostazioni AI' })).toBeVisible()
  await expect(page.getByRole('combobox', { name: 'Modello AI' })).toHaveCount(0)
  await expect(page.getByText('Usato per chat, dati e compilazione.', { exact: false })).toHaveCount(0)
  await page.getByRole('textbox', { name: 'Messaggio per Mapi RAG' }).fill('Quali dati mancano?')
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-composer-gear.png`, fullPage: true })
  await gear.click()
  const menu = page.getByRole('menu', { name: 'Modello AI' })
  await expect(menu).toBeVisible()
  const bounds = await menu.boundingBox()
  const viewport = page.viewportSize()!
  expect(bounds!.x).toBeGreaterThanOrEqual(0)
  expect(bounds!.y).toBeGreaterThanOrEqual(0)
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(viewport.width)
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport.height)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-composer-model-menu.png`, fullPage: true })
  await page.getByRole('menuitemradio', { name: /Ollama locale/ }).click()
  await expect(menu).toHaveCount(0)
  await expect(gear).toHaveAttribute('title', 'Modello: Ollama locale · modello-locale')
  await expect(page.getByRole('textbox')).toHaveValue('Quali dati mancano?')
  expect(answers).toBe(0)
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByText('Risposta Mapi', { exact: true })).toBeVisible()
  await expect(page.locator('.composer--docked')).toBeVisible()
  await expect(gear).toHaveAttribute('title', 'Modello: Ollama locale · modello-locale')
  await gear.click()
  await expect(page.getByRole('menuitemradio', { name: /Ollama locale/ })).toHaveAttribute('aria-checked', 'true')
  await page.keyboard.press('Escape')
  await expect(gear).toBeFocused()
  await expect(menu).toHaveCount(0)
  expect(answers).toBe(1)
})
