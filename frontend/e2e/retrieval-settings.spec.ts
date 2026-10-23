import { expect, test } from '@playwright/test'
import embeddingProviders from './embedding-providers.fixture.json' with { type: 'json' }

const initial = {
  backend: 'fts5', qdrant_mode: 'local', qdrant_url: 'http://127.0.0.1:6333',
  embedding_url: 'http://127.0.0.1:11434', embedding_model: 'bge-m3',
  query_prefix: 'query:', document_prefix: 'passage:', has_qdrant_api_key: false, has_embedding_api_key: false,
}

test('two cards, installed embedding models and separate check/save/index actions', async ({ page }, testInfo) => {
  let settings = { ...initial }
  let fail = true
  let saves = 0
  let checks = 0
  let indexUpdates = 0
  let inventories = 0
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/retrieval/providers') return route.fulfill({ json: embeddingProviders })
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path === '/api/settings/retrieval/models') {
      inventories += 1
      expect(Object.keys(route.request().postDataJSON()).sort()).toEqual(['clear_embedding_api_key', 'embedding_api_key', 'embedding_provider', 'embedding_url'])
      return route.fulfill({ json: { models: ['bge-m3:latest', 'nomic-embed-text:latest'] } })
    }
    if (path === '/api/settings/retrieval/check') {
      checks += 1
      const payload = route.request().postDataJSON()
      expect(payload.embedding_model).toBe('nomic-embed-text:latest')
      expect(payload.qdrant_api_key).toBe('browser-fake-secret')
      return route.fulfill({ json: { message: 'Collegamento riuscito.', dimensions: 768 } })
    }
    if (path === '/api/settings/retrieval/index') {
      indexUpdates += 1
      if (fail) { fail = false; return route.fulfill({ status: 502, json: { detail: 'Servizio temporaneamente non raggiungibile' } }) }
      return route.fulfill({ json: { indexed_chunks: 306, updated_chunks: 3, deleted_chunks: 1 } })
    }
    if (path === '/api/settings/retrieval') {
      if (route.request().method() === 'PUT') {
        saves += 1
        const { qdrant_api_key, embedding_api_key: _key, clear_qdrant_api_key: _clear,
          clear_embedding_api_key: _clearEmbedding, ...config } = route.request().postDataJSON()
        expect(config.query_prefix).toBe('query:')
        expect(config.document_prefix).toBe('passage:')
        expect(config).not.toHaveProperty('has_qdrant_api_key')
        settings = { ...config, has_qdrant_api_key: !!qdrant_api_key || settings.has_qdrant_api_key, has_embedding_api_key: false }
      }
      return route.fulfill({ json: settings })
    }
    return route.fulfill({ json: [] })
  })
  await page.goto('/settings')
  const search = page.getByRole('region', { name: 'Ricerca nelle fonti' })
  const embedding = page.getByRole('region', { name: 'Modelli di embedding' })
  await expect(search).toBeVisible()
  await expect(page.getByRole('heading', { level: 2 })).toHaveText(['Modelli AI', 'Modelli di embedding', 'Ricerca nelle fonti'])
  await expect(embedding).toBeVisible()
  await expect(embedding.getByLabel('Modello di embedding')).toBeEnabled()
  await expect(embedding.getByLabel('Modello di embedding')).toHaveValue('bge-m3')
  expect(inventories).toBe(1)
  await expect(search.getByText('Impostazioni avanzate', { exact: true })).toHaveCount(0)
  await search.getByLabel('Metodo di ricerca').selectOption('qdrant')
  await expect(search.getByRole('option', { name: 'Semantica', exact: true })).toHaveCount(1)
  await expect(page.getByText(/Trova passaggi con un significato/)).toHaveCount(0)
  await expect(page.getByText(/Qdrant funziona nel backend/)).toHaveCount(0)
  await expect(page.getByText(/Nome di un modello di embedding già installato/)).toHaveCount(0)
  await expect(search.getByLabel('Tipo di archivio')).toBeHidden()
  await expect(embedding.getByLabel('Indirizzo Ollama')).toBeHidden()
  await embedding.getByLabel('Modello di embedding').selectOption('nomic-embed-text:latest')
  await expect(embedding.getByText(/Questa modifica può richiedere/)).toBeVisible()
  await search.getByText('Impostazioni avanzate', { exact: true }).click()
  await embedding.getByText('Impostazioni avanzate', { exact: true }).click()
  await expect(search.getByLabel('Indirizzo Qdrant')).toHaveCount(0)
  await expect(search.getByRole('button', { name: 'Aggiorna indice' })).toBeDisabled()
  await search.getByLabel('Tipo di archivio').selectOption('remote')
  await search.getByLabel('Indirizzo Qdrant').fill('https://qdrant.example.test')
  await search.getByLabel('Chiave Qdrant (facoltativa)').fill('browser-fake-secret')
  await embedding.getByLabel('Indirizzo Ollama').fill('')
  await embedding.getByText('Impostazioni avanzate', { exact: true }).click()
  await search.getByRole('button', { name: 'Salva impostazioni' }).click()
  await expect(embedding.getByLabel('Indirizzo Ollama')).toBeVisible()
  expect(saves).toBe(0)
  await embedding.getByLabel('Indirizzo Ollama').fill('http://127.0.0.1:11434')
  await search.getByRole('button', { name: 'Verifica collegamento' }).click()
  await expect(search.getByRole('status')).toContainText('Collegamento riuscito')
  expect(checks).toBe(1)
  expect(saves).toBe(0)
  expect(indexUpdates).toBe(0)
  await search.getByRole('button', { name: 'Salva impostazioni' }).click()
  await expect(search.getByRole('button', { name: 'Aggiorna indice' })).toBeEnabled()
  await expect(search.getByLabel('Chiave Qdrant (facoltativa)')).toHaveValue('')
  expect(indexUpdates).toBe(0)
  await search.getByRole('button', { name: 'Aggiorna indice' }).click()
  await expect(search.getByRole('alert')).toContainText('temporaneamente non raggiungibile')
  await search.getByRole('button', { name: 'Aggiorna indice' }).click()
  await expect(search.getByRole('status')).toContainText('306 frammenti')
  expect(indexUpdates).toBe(2)
  await page.reload()
  await expect(search.getByLabel('Metodo di ricerca')).toHaveValue('qdrant')
  await expect(search.getByLabel('Tipo di archivio')).toBeHidden()
  await expect(embedding.getByLabel('Modello di embedding')).toHaveValue('nomic-embed-text:latest')
  await expect(embedding.getByLabel('Modello di embedding')).toBeEnabled()
  await expect(embedding.getByLabel('Indirizzo Ollama')).toBeHidden()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-retrieval-two-cards.png`, fullPage: true })
  await search.getByLabel('Metodo di ricerca').selectOption('fts5')
  await search.getByRole('button', { name: 'Salva impostazioni' }).click()
  await expect(search.getByRole('status')).toHaveText('Impostazioni salvate. La ricerca usa le parole chiave.')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
})

test('advanced panels inherit light tokens and fit narrow screens', async ({ page }, testInfo) => {
  await page.route('**/api/**', (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/retrieval/providers') return route.fulfill({ json: embeddingProviders })
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path === '/api/settings/retrieval') return route.fulfill({ json: { ...initial, backend: 'qdrant' } })
    if (path === '/api/settings/retrieval/models') return route.fulfill({ json: { models: ['bge-m3:latest', 'another-embedding'] } })
    return route.fulfill({ json: [] })
  })
  if (testInfo.project.name === 'mobile') await page.setViewportSize({ width: 320, height: 915 })
  await page.emulateMedia({ colorScheme: 'light' })
  await page.goto('/settings')
  await page.addStyleTag({ content: `:root {
    color-scheme: light; --bg: #f7f7f2; --panel: #fff; --panel-muted: #fafaf7;
    --control: #ecece6; --control-hover: #e1e1db; --border: #d8d8d0; --border-strong: #bcbcb4;
    --text: #242520; --text-strong: #141511; --text-muted: #5d5e57;
    --paper: #f4f2ec; --paper-text: #242520; --blue: #315d86;
  }` })
  const search = page.getByRole('region', { name: 'Ricerca nelle fonti' })
  const embedding = page.getByRole('region', { name: 'Modelli di embedding' })
  await search.getByText('Impostazioni avanzate', { exact: true }).click()
  await embedding.getByText('Impostazioni avanzate', { exact: true }).click()
  await expect(embedding.getByLabel('Modello di embedding')).toBeEnabled()
  await embedding.getByLabel('Modello di embedding').selectOption('another-embedding')
  const model = embedding.getByLabel('Modello di embedding')
  expect(await model.evaluate((element) => getComputedStyle(element).color)).toBe('rgb(36, 37, 32)')
  expect(await model.evaluate((element) => getComputedStyle(element).backgroundColor)).toBe('rgb(250, 250, 247)')
  expect(await embedding.getByText(/Questa modifica può richiedere/).evaluate((element) => getComputedStyle(element).color)).toBe('rgb(121, 81, 16)')
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-retrieval-two-cards-light.png`, fullPage: true })
})

test('configure an independent cloud embedding provider without changing chat settings', async ({ page }, testInfo) => {
  let saved = { ...initial, embedding_provider: 'ollama', backend: 'qdrant', has_embedding_api_key: true }
  let modelReads = 0
  let indexUpdates = 0
  await page.route('**/api/**', (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path === '/api/settings/retrieval/providers') return route.fulfill({ json: embeddingProviders })
    if (path === '/api/settings/retrieval/models') {
      modelReads += 1
      const payload = route.request().postDataJSON()
      if (payload.embedding_provider === 'openai') {
        expect(payload.embedding_api_key).toBe(saved.embedding_provider === 'openai' ? '' : 'new-cloud-embedding-key')
        expect(payload.embedding_url).toBe('https://api.openai.com/v1')
      }
      return route.fulfill({ json: { models: payload.embedding_provider === 'openai'
        ? ['text-embedding-3-small', 'text-embedding-3-large'] : ['bge-m3:latest'] } })
    }
    if (path === '/api/settings/retrieval/index') {
      indexUpdates += 1
      return route.fulfill({ status: 500, json: { detail: 'Non deve essere chiamato' } })
    }
    if (path === '/api/settings/retrieval') {
      if (route.request().method() === 'PUT') {
        const { embedding_api_key: key, qdrant_api_key: _q, clear_embedding_api_key: _clear,
          clear_qdrant_api_key: _clearQ, ...config } = route.request().postDataJSON()
        expect(key).toBe('new-cloud-embedding-key')
        expect(config.embedding_provider).toBe('openai')
        expect(config.embedding_model).toBe('text-embedding-3-large')
        saved = { ...config, has_embedding_api_key: true, has_qdrant_api_key: false }
      }
      return route.fulfill({ json: saved })
    }
    expect(path).not.toContain('/settings/ai/')
    return route.fulfill({ json: [] })
  })
  await page.goto('/settings')
  await expect(page.getByRole('heading', { level: 2 })).toHaveText(['Modelli AI', 'Modelli di embedding', 'Ricerca nelle fonti'])
  const embedding = page.getByRole('region', { name: 'Modelli di embedding' })
  const search = page.getByRole('region', { name: 'Ricerca nelle fonti' })
  await expect(embedding.getByLabel('Modello di embedding')).toBeEnabled()
  await embedding.getByLabel('Provider di embedding').selectOption('openai')
  const key = embedding.getByLabel('Chiave del servizio embedding', { exact: true })
  await expect(key).toBeVisible()
  await expect(key).toHaveValue('')
  await expect(key).toBeEnabled()
  await expect(key).toHaveAttribute('type', 'password')
  await expect(key).toHaveAttribute('required')
  expect(modelReads).toBe(1)
  await key.fill('new-cloud-embedding-key')
  await embedding.getByRole('button', { name: 'Ricarica modelli' }).click()
  await expect(embedding.getByLabel('Modello di embedding')).toBeEnabled()
  await embedding.getByLabel('Modello di embedding').selectOption('text-embedding-3-large')
  await search.getByRole('button', { name: 'Salva impostazioni' }).click()
  await expect(search.getByRole('status')).toContainText('Impostazioni salvate')
  await expect(key).toHaveValue('')
  expect(indexUpdates).toBe(0)
  expect(await page.evaluate(() => JSON.stringify(localStorage))).not.toContain('new-cloud-embedding-key')
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-embedding-providers.png`, fullPage: true })
})
