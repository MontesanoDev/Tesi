import { expect, test } from '@playwright/test'

test('multiple originals persist separately from sources, with download and partial failures', async ({ page }, testInfo) => {
  const forms: { id: number; name: string; metadata: string; kind: string; status: string; byte_size: number; page_count: number; chunk_count: number }[] = []
  const original = Buffer.from('Ragione sociale: ___\r\nPEC: ___\r\n', 'utf8')
  const projectId = 'moduli-test'
  let failRemoval = true
  let uploads = 0
  const unexpected: string[] = []
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    const root = `/api/projects/${projectId}`
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
    if (path === root) return route.fulfill({ json: {
      id: projectId, title: 'Moduli della candidatura', description: 'Archivio degli originali',
      status: 'In analisi', status_tone: 'info', updated_label: '', source_count: 1, model_count: forms.length,
      instructions: '', call_fact_count: 0, missing_fact_count: 0, knowledge_sources: [], conversations: [],
      files: [{ id: 1, name: 'bando.pdf', kind: 'source', metadata: 'PDF · 2 frammenti', status: 'Indicizzato', page_count: 1, chunk_count: 2 }, ...forms],
    } })
    if (path === `${root}/forms` && route.request().method() === 'POST') {
      uploads += 1
      const body = route.request().postDataBuffer()!.toString()
      const name = /filename="([^"]+)"/.exec(body)![1]
      if (name === 'danneggiato.txt') return route.fulfill({ status: 422, json: { detail: 'Testo non leggibile' } })
      const format = name.endsWith('.docx') ? 'DOCX' : 'TXT'
      const item = { id: uploads + 10, name, kind: 'form', metadata: `${format} · 35 B`, status: 'Caricato',
        byte_size: original.length, page_count: 0, chunk_count: 0 }
      forms.push(item)
      return route.fulfill({ status: 201, json: item })
    }
    if (path.startsWith(`${root}/forms/`)) {
      const id = Number(path.split('/')[5])
      const index = forms.findIndex((item) => item.id === id)
      if (index < 0) return route.fulfill({ status: 404, json: { detail: 'Modulo non trovato' } })
      if (path.endsWith('/download')) return route.fulfill({ body: original, contentType: 'text/plain' })
      if (route.request().method() === 'DELETE') {
        if (failRemoval) {
          failRemoval = false
          return route.fulfill({ status: 500, json: { detail: 'File occupato; riprova' } })
        }
        forms.splice(index, 1)
        return route.fulfill({ status: 204 })
      }
    }
    unexpected.push(path)
    return route.fulfill({ status: 404, json: { detail: 'Richiesta inattesa' } })
  })
  await page.goto(`/projects/${projectId}`)
  const panel = page.getByRole('region', { name: 'Moduli da compilare' })
  await expect(panel.getByText('Nessun modulo caricato')).toBeVisible()
  await expect(panel.getByText('0 moduli', { exact: true })).toBeVisible()
  await expect(panel.getByText(/I PDF possono/)).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Compila Word' })).toHaveCount(0)
  await expect(page.getByLabel('Seleziona moduli da compilare')).toHaveAttribute('accept', '.docx,.txt')
  await page.getByLabel('Seleziona moduli da compilare').setInputFiles([
    { name: 'domanda.txt', mimeType: 'text/plain', buffer: original },
    { name: 'danneggiato.txt', mimeType: 'text/plain', buffer: Buffer.from('invalid') },
    { name: 'modulo.pdf', mimeType: 'application/pdf', buffer: Buffer.from('unsupported') },
    { name: 'modulo.md', mimeType: 'text/markdown', buffer: original },
    { name: 'dichiarazione.docx', mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', buffer: original },
  ])
  await expect(panel.getByText('2 moduli caricati.')).toBeVisible()
  await expect(panel.getByText('2 moduli', { exact: true })).toBeVisible()
  await expect(panel.getByRole('alert')).toContainText('danneggiato.txt: Testo non leggibile')
  await expect(panel.getByRole('alert')).toContainText('modulo.pdf: Usa un file Word (.docx) o testo (.txt)')
  await expect(panel.getByRole('alert')).toContainText('modulo.md: Usa un file Word (.docx) o testo (.txt)')
  await expect(panel.getByText('domanda.txt', { exact: true })).toBeVisible()
  await expect(panel.getByText('dichiarazione.docx', { exact: true })).toBeVisible()
  await expect(page.locator('.knowledge-files')).toContainText('1 fonte')
  await expect(page.locator('.knowledge-files').getByText('domanda.txt')).toHaveCount(0)
  await expect(page.locator('.knowledge-files').getByText('bando.pdf')).toBeVisible()
  expect(uploads).toBe(3)

  await page.reload()
  await expect(panel.getByRole('button', { name: 'Scarica originale domanda.txt' })).toBeVisible()
  const pending = page.waitForEvent('download')
  await panel.getByRole('button', { name: 'Scarica originale domanda.txt' }).click()
  const download = await pending
  expect(download.suggestedFilename()).toBe('domanda.txt')
  const stream = await download.createReadStream()
  const chunks: Buffer[] = []
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk))
  expect(Buffer.concat(chunks)).toEqual(original)
  await panel.getByRole('button', { name: 'Rimuovi domanda.txt', exact: true }).click()
  await panel.getByRole('button', { name: 'Annulla' }).click()
  expect(forms).toHaveLength(2)
  await panel.getByRole('button', { name: 'Rimuovi domanda.txt', exact: true }).click()
  await panel.getByRole('button', { name: 'Rimuovi modulo', exact: true }).click()
  await expect(panel.getByRole('alert')).toHaveText('File occupato; riprova')
  expect(forms).toHaveLength(2)
  await panel.getByRole('button', { name: 'Rimuovi modulo', exact: true }).click()
  await expect(panel.getByText('domanda.txt', { exact: true })).toHaveCount(0)
  await expect(panel.getByText('dichiarazione.docx', { exact: true })).toBeVisible()
  await page.reload()
  await expect(panel.locator('.project-forms-list > li')).toHaveCount(1)
  await expect(panel.getByText('1 modulo', { exact: true })).toBeVisible()
  await expect(page.getByLabel('Messaggio per Mapi RAG')).toBeVisible()
  expect(unexpected).toEqual([])
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-project-forms.png`, fullPage: true })
})
