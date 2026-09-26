import { expect, test } from '@playwright/test'
import providers from './ai-providers.fixture.json' with { type: 'json' }

test('choose a provider, save Claude and connect OpenRouter from the browser', async ({ page }, testInfo) => {
  const profiles: Record<string, unknown>[] = []
  const errors: string[] = []
  const loginToken = 'temporary-browser-connection-token'
  page.on('pageerror', (error) => errors.push(error.message))
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { providers, profiles, default_profile_id: profiles[0]?.id ?? null } })
    if (path === '/api/settings/ai/openrouter/login') return route.fulfill({ json: {
      connection_token: loginToken, authorization_url: 'https://openrouter.ai/auth?code_challenge=browser-test&code_challenge_method=S256', expires_in: 600,
    } })
    if (path === '/api/settings/ai/openrouter/login/complete') {
      expect(route.request().postDataJSON()).toEqual({ connection_token: loginToken, code: 'browser-test-code' })
      return route.fulfill({ json: { message: 'Account collegato' } })
    }
    if (path === '/api/settings/ai/check') {
      const payload = route.request().postDataJSON()
      if (payload.provider === 'openrouter') {
        expect(payload.connection_token).toBe(loginToken)
        expect(payload.api_key).toBe('')
      } else {
        expect(payload.provider).toBe('anthropic')
        expect(payload.api_key).toBe('browser-fake-key')
      }
      return route.fulfill({ json: { models: [payload.provider === 'anthropic' ? 'claude-test' : 'test/remote-model'], message: 'Collegamento riuscito.' } })
    }
    if (path === '/api/settings/ai/profiles') {
      const { api_key: key, connection_token: token, clear_api_key: clear, ...payload } = route.request().postDataJSON()
      if (payload.provider === 'openrouter') { expect(token).toBe(loginToken); expect(key).toBe('') }
      expect(clear).toBe(false)
      const profile = { ...payload, id: `model-${profiles.length}`, has_api_key: true }
      profiles.push(profile)
      return route.fulfill({ status: 201, json: profile })
    }
    return route.fulfill({ json: [] })
  })
  await page.goto('/settings')
  await page.getByRole('button', { name: 'Aggiungi modello' }).click()
  for (const provider of providers) {
    await expect(page.getByRole('combobox', { name: 'Servizio', exact: true }).locator(`option[value="${provider.id}"]`)).toHaveText(provider.name)
  }
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-ai-providers.png`, fullPage: true })
  await page.getByRole('combobox', { name: 'Servizio', exact: true }).selectOption('ollama')
  const endpoint = page.getByRole('textbox', { name: /^Indirizzo del servizio/ })
  await expect(endpoint).toBeVisible()
  await expect(page.getByText('Ollama può essere sul computer che esegue Mapi', { exact: false })).toBeVisible()
  await endpoint.fill('https://ollama.example.test')
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-ollama-endpoint.png`, fullPage: true })
  await page.getByRole('combobox', { name: 'Servizio', exact: true }).selectOption('anthropic')
  await expect(page.getByRole('combobox', { name: 'Servizio', exact: true })).toHaveValue('anthropic')
  await expect(page.getByRole('link', { name: /Ottieni una chiave/ })).toHaveAttribute('href', 'https://platform.claude.com/settings/keys')
  await page.getByLabel('Chiave API', { exact: true }).fill('browser-fake-key')
  await page.getByRole('button', { name: 'Verifica collegamento e trova modelli' }).click()
  await expect(page.getByLabel('Modello', { exact: true })).toHaveValue('claude-test')
  await page.getByRole('button', { name: 'Salva modello' }).click()
  await expect(page.locator('.ai-profile-list')).toContainText('claude-test')
  await page.getByRole('button', { name: 'Aggiungi modello' }).click()
  await page.getByRole('combobox', { name: 'Servizio', exact: true }).selectOption('openrouter')
  await page.getByRole('button', { name: 'Accedi con OpenRouter' }).click()
  await expect(page.getByRole('link', { name: /Apri accesso OpenRouter/ })).toHaveAttribute('href', /code_challenge=browser-test/)
  await page.getByLabel('Codice di autorizzazione').fill('browser-test-code')
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-openrouter-login.png`, fullPage: true })
  await page.getByRole('button', { name: 'Collega account' }).click()
  await expect(page.getByLabel('Modello', { exact: true })).toHaveValue('test/remote-model')
  await expect(page.getByLabel('Chiave API', { exact: true })).toHaveCount(0)
  await expect(page.getByLabel('Codice di autorizzazione')).toHaveCount(0)
  await page.getByRole('button', { name: 'Salva modello' }).click()
  await expect(page.locator('.ai-profile-list')).toContainText('test/remote-model')
  await page.reload()
  await expect(page.locator('.ai-profile-list li')).toHaveCount(2)
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toMatch(/browser-fake-key|browser-test-code|temporary-browser-connection-token/)
  expect(errors).toEqual([])
})
