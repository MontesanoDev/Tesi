import { expect, test } from '@playwright/test'

for (const outcome of ['success', 'failure'] as const) {
  test(`document button stays visually stable during thinking save (${outcome})`, async ({ page }, testInfo) => {
    const profile = { id: 'cloud', name: 'DeepSeek', provider: 'deepseek', model: 'deepseek-flash',
      base_url: 'https://provider.test', context_window: 32768, has_api_key: true }
    let finish!: () => void
    const pending = new Promise<void>((resolve) => { finish = resolve })
    let answers = 0
    await page.route('**/api/**', async (route) => {
      const path = new URL(route.request().url()).pathname
      if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [profile], default_profile_id: profile.id } })
      if (path.endsWith('/ai-model')) {
        if (route.request().method() === 'PUT') {
          expect(route.request().postDataJSON()).toEqual({ profile_id: null, thinking: true })
          await pending
          if (outcome === 'failure') return route.fulfill({ status: 502, json: { detail: 'Salvataggio non riuscito' } })
          return route.fulfill({ json: { profile_id: null, effective_profile: profile, thinking: true } })
        }
        return route.fulfill({ json: { profile_id: null, effective_profile: profile, thinking: false } })
      }
      if (path === '/api/projects/plus-ui') return route.fulfill({ json: {
        id: 'plus-ui', title: 'Progetto di prova', description: '', status: 'Bozza', status_tone: 'info',
        updated_label: '', source_count: 1, model_count: 0, instructions: '', call_fact_count: 0,
        missing_fact_count: 0, knowledge_sources: [], conversations: [], files: [
          { id: 42, name: 'modulo-test.docx', kind: 'form', metadata: 'DOCX', status: 'Indicizzato' },
        ],
      } })
      if (path.endsWith('/answer')) answers += 1
      return route.fulfill({ json: [] })
    })
    await page.goto('/projects/plus-ui')
    const plus = page.getByRole('button', { name: 'Aggiungi un documento' })
    const toggle = page.getByRole('switch', { name: 'Ragionamento approfondito' })
    const send = page.getByRole('button', { name: 'Invia', exact: true })
    const input = page.getByRole('textbox', { name: 'Messaggio per l’assistente' })
    await expect(plus).toBeEnabled()
    await expect(toggle).toBeEnabled()
    await input.fill('Testo conservato')
    const before = await plus.evaluate((button) => {
      const s = getComputedStyle(button)
      return { opacity: s.opacity, background: s.backgroundColor, color: s.color }
    })
    await toggle.click()
    await expect(toggle).toBeDisabled()
    await expect(send).toBeDisabled()
    const during = await plus.evaluate((button) => {
      const s = getComputedStyle(button)
      return { opacity: s.opacity, background: s.backgroundColor, color: s.color }
    })
    await testInfo.attach('plus-styles', { body: JSON.stringify({ before, during }), contentType: 'application/json' })
    expect(during).toEqual(before)
    await expect(plus).toBeEnabled()
    await expect(plus).not.toHaveClass(/is-active/)
    // Selecting a reference is local. It must not submit while the preference is pending.
    await plus.click()
    await page.getByRole('option', { name: /modulo-test.docx/ }).click()
    await expect(page.getByRole('button', { name: 'Rimuovi riferimento al documento' })).toBeVisible()
    await expect(send).toBeDisabled()
    expect(answers).toBe(0)
    finish()
    await expect(toggle).toBeEnabled()
    await expect(toggle).toHaveAttribute('aria-checked', outcome === 'success' ? 'true' : 'false')
    await expect(send).toBeEnabled()
    await expect(input).toHaveValue('Testo conservato')
    await expect(plus).toBeEnabled()
    expect(answers).toBe(0)
  })
}

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
        thinking = body.thinking ?? thinking
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
  await page.getByRole('textbox', { name: 'Messaggio per l’assistente' }).fill('Quali dati mancano?')
  const toggle = page.getByRole('switch', { name: 'Ragionamento approfondito' })
  await expect(toggle).toBeEnabled()
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  expect(selected).toBeNull()
  expect(answers).toBe(0)
  await page.reload()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  await page.getByRole('textbox', { name: 'Messaggio per l’assistente' }).fill('Quali dati mancano?')
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-composer-gear.png`, fullPage: true })
  await gear.click()
  const menu = page.getByRole('menu', { name: 'Modello AI' })
  await expect(menu).toBeVisible()
  await expect(page.getByRole('menuitemradio', { name: /Usa predefinito/ }))
    .toHaveAttribute('aria-checked', 'true')
  const bounds = await menu.boundingBox()
  const viewport = page.viewportSize()!
  expect(bounds!.x).toBeGreaterThanOrEqual(0)
  expect(bounds!.y).toBeGreaterThanOrEqual(0)
  expect(bounds!.x + bounds!.width).toBeLessThanOrEqual(viewport.width)
  expect(bounds!.y + bounds!.height).toBeLessThanOrEqual(viewport.height)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-composer-model-menu.png`, fullPage: true })
  await page.getByRole('menuitemradio', { name: /^DeepSeek/ }).click()
  await expect(toggle).toBeEnabled()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'false')
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  await expect(menu).toHaveCount(0)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-composer-thinking.png`, fullPage: true })
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'false')
  await gear.click()
  await page.getByRole('menuitemradio', { name: /Usa predefinito/ }).click()
  await expect(toggle).toHaveAttribute('aria-checked', 'false')
  await toggle.click()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  expect(selected).toBeNull()
  await expect(page.getByRole('textbox')).toHaveValue('Quali dati mancano?')
  expect(answers).toBe(0)
  await gear.click()
  await page.getByRole('menuitemradio', { name: /Ollama locale/ }).click()
  await expect(menu).toHaveCount(0)
  await expect(toggle).toHaveCount(0)
  await expect(gear).toHaveAttribute('title', 'Modello: Ollama locale · modello-locale')
  await expect(page.getByRole('textbox')).toHaveValue('Quali dati mancano?')
  expect(answers).toBe(0)
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByText('Risposta', { exact: true })).toBeVisible()
  await expect(page.locator('.composer--docked')).toBeVisible()
  await expect(gear).toHaveAttribute('title', 'Modello: Ollama locale · modello-locale')
  await gear.click()
  await expect(page.getByRole('menuitemradio', { name: /Ollama locale/ })).toHaveAttribute('aria-checked', 'true')
  await page.keyboard.press('Escape')
  await expect(gear).toBeFocused()
  await expect(menu).toHaveCount(0)
  await gear.click()
  await page.getByRole('menuitemradio', { name: /Usa predefinito/ }).click()
  await expect(toggle).toBeEnabled()
  await expect(toggle).toHaveAttribute('aria-checked', 'true')
  expect(selected).toBeNull()
  expect(answers).toBe(1)
})
