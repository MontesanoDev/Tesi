import { expect, test } from '@playwright/test'

test('the composer selects models and thinking without submitting the chat', async ({ page }, testInfo) => {
  const profiles = [
    { id: 'cloud', name: 'DeepSeek', provider: 'deepseek', model: 'deepseek-v4-flash',
      base_url: 'https://provider.test', context_window: 32768, has_api_key: true },
    { id: 'local', name: 'Ollama locale', provider: 'ollama', model: 'modello-locale',
      base_url: 'http://127.0.0.1:11434', context_window: 32768, has_api_key: false },
  ]
  let selected: string | null = null
  let thinking = false
  let answers = 0
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles, default_profile_id: 'cloud' } })
    if (path.endsWith('/ai-model')) {
      if (route.request().method() === 'PUT') {
        const body = route.request().postDataJSON()
        selected = body.profile_id
        thinking = selected === null ? false : body.thinking ?? thinking
      }
      return route.fulfill({ json: { profile_id: selected,
        effective_profile: profiles.find((profile) => profile.id === (selected ?? 'cloud')), thinking } })
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
  const toggle = page.getByRole('switch', { name: 'Ragionamento approfondito' })
  await expect(toggle).toBeDisabled()
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
  await page.getByRole('menuitemradio', { name: /^DeepSeek/ }).click()
  await expect(toggle).toBeEnabled()
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  await expect(menu).toHaveCount(0)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-composer-thinking.png`, fullPage: true })
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'false')
  await expect(page.getByRole('textbox')).toHaveValue('Quali dati mancano?')
  expect(answers).toBe(0)
  await gear.click()
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
