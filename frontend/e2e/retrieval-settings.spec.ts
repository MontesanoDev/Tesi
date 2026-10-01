import { expect, test } from '@playwright/test'

test('configure vector search, check a remote endpoint and prepare the saved index', async ({ page }, testInfo) => {
  let settings = {
    backend: 'fts5', qdrant_mode: 'local', qdrant_url: 'http://127.0.0.1:6333',
    embedding_url: 'http://127.0.0.1:11434', embedding_model: 'embeddinggemma',
    query_prefix: '', document_prefix: '', has_qdrant_api_key: false, has_embedding_api_key: false,
  }
  let fail = true
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path === '/api/settings/retrieval/check') {
      const payload = route.request().postDataJSON()
      expect(payload.embedding_model).toBe('embeddinggemma')
      expect(payload.qdrant_api_key).toBe('browser-fake-secret')
      return route.fulfill({ json: { message: 'Collegamento riuscito.', dimensions: 768 } })
    }
    if (path === '/api/settings/retrieval/index') {
      if (fail) { fail = false; return route.fulfill({ status: 502, json: { detail: 'Servizio temporaneamente non raggiungibile' } }) }
      return route.fulfill({ json: { indexed_chunks: 306, updated_chunks: 3, deleted_chunks: 1 } })
    }
    if (path === '/api/settings/retrieval') {
      if (route.request().method() === 'PUT') {
        const { qdrant_api_key, embedding_api_key: _key, clear_qdrant_api_key: _clear,
          clear_embedding_api_key: _clearEmbedding, ...config } = route.request().postDataJSON()
        expect(config).not.toHaveProperty('has_qdrant_api_key')
        settings = { ...config, has_qdrant_api_key: !!qdrant_api_key, has_embedding_api_key: false }
      }
      return route.fulfill({ json: settings })
    }
    return route.fulfill({ json: [] })
  })
  await page.goto('/settings')
  const panel = page.getByRole('region', { name: 'Ricerca nelle fonti' })
  await panel.getByLabel('Metodo di ricerca').selectOption('qdrant')
  await expect(panel.getByLabel('Archivio vettoriale')).toBeHidden()
  await expect(panel.getByRole('button', { name: 'Aggiorna indice' })).toBeHidden()
  await expect(panel.getByRole('button', { name: 'Salva ricerca' })).toBeVisible()
  await panel.getByText('Impostazioni avanzate', { exact: true }).click()
  await expect(panel.getByText('embeddinggemma', { exact: true })).toBeVisible()
  await expect(panel.getByLabel('Modello di embedding')).toHaveCount(0)
  await expect(panel.getByLabel(/Prefisso/)).toHaveCount(0)
  await expect(panel.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
  await panel.getByLabel('Archivio vettoriale').selectOption('remote')
  await panel.getByLabel('Indirizzo Qdrant').fill('https://qdrant.example.test')
  await panel.getByLabel(/Chiave Qdrant/).fill('browser-fake-secret')
  // A required field hidden by the disclosure must still be reachable on submit.
  await panel.getByLabel(/Indirizzo Ollama/).fill('')
  await panel.getByText('Impostazioni avanzate', { exact: true }).click()
  await panel.getByRole('button', { name: 'Salva ricerca' }).click()
  await expect(panel.getByLabel(/Indirizzo Ollama/)).toBeVisible()
  await panel.getByLabel(/Indirizzo Ollama/).fill('http://127.0.0.1:11434')
  await panel.getByRole('button', { name: 'Verifica collegamento' }).click()
  await expect(panel.getByRole('status')).toContainText('Collegamento riuscito')
  await panel.getByRole('button', { name: 'Salva ricerca' }).click()
  await expect(panel.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled()
  await expect(panel.getByLabel(/Chiave Qdrant/)).toHaveValue('')
  await panel.getByRole('button', { name: 'Aggiorna indice' }).click()
  await expect(panel.getByRole('alert')).toContainText('temporaneamente non raggiungibile')
  await expect(panel.getByLabel('Metodo di ricerca')).toHaveValue('qdrant')
  await panel.getByRole('button', { name: 'Aggiorna indice' }).click()
  await expect(panel.getByRole('status')).toContainText('306 frammenti')
  await page.reload()
  await expect(panel.getByLabel('Metodo di ricerca')).toHaveValue('qdrant')
  await expect(panel.getByLabel('Archivio vettoriale')).toBeHidden()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  await panel.scrollIntoViewIfNeeded()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-retrieval-settings.png`, fullPage: true })
  await panel.getByLabel('Metodo di ricerca').selectOption('fts5')
  await panel.getByRole('button', { name: 'Salva ricerca' }).click()
  await expect(panel.getByRole('status')).toHaveText('Ricerca lessicale salvata.')
})
