import { expect, test, type Page } from '@playwright/test'
import { readFile } from 'node:fs/promises'
import { documentCompilationFixture } from '../src/test/documentCompilationFixture'
import type { DocumentCompilation } from '../src/types'

const modelPath = '../demo-documents/bandi/catanzaro-dl-cse/modello/domanda-partecipazione.docx'
const url = '/projects/docx-test/knowledge?artifact=template'

async function fixture(page: Page, existing = false) {
  const run = documentCompilationFixture()
  const state = { runs: existing ? [run] : [] as DocumentCompilation[], generations: 0, fail: false, payload: '', downloads: [] as string[] }
  const model = await readFile(modelPath)
  const artifacts = ['call_facts', 'project_facts', 'template', 'output_draft'].map((kind, i) => ({
    id: `docx-test--${kind}`, kind, scope: 'project', title: ['Call Facts', 'Dati del progetto', 'Template', 'Draft'][i],
    filename: `${kind}.md`, content: '# Modello testuale precedente', version: 1, byte_size: 100,
    editable: true, updated_at: '', chunk_count: 0, status: kind === 'output_draft' ? 'Da generare' : 'Bozza',
  }))
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    const root = '/api/projects/docx-test'
    if (path === root) return route.fulfill({ json: {
      id: 'docx-test', title: 'Residenze universitarie di Catanzaro', description: 'Direzione lavori e sicurezza',
      status: 'In analisi', status_tone: 'info', updated_label: 'Ora', source_count: 2, model_count: 0,
      instructions: '', call_fact_count: 0, missing_fact_count: 0,
      files: [], knowledge_sources: [], conversations: [],
    } })
    if (path === `${root}/artifacts`) return route.fulfill({ json: artifacts })
    const artifact = artifacts.find((item) => path === `${root}/artifacts/${item.id}`)
    if (artifact) return route.fulfill({ json: artifact })
    if (path === `${root}/document-compilations`) {
      if (route.request().method() === 'POST') {
        state.generations += 1
        state.payload = route.request().postDataBuffer()?.toString('utf-8') ?? ''
        if (state.fail) return route.fulfill({ status: 502, json: { detail: 'Risposta del modello non valida' } })
        const next = documentCompilationFixture('docx-test', `run-${state.runs.length + 1}`)
        state.runs.unshift(next)
        return route.fulfill({ status: 201, json: next })
      }
      return route.fulfill({ json: state.runs.map(({ report: _report, ...summary }) => summary) })
    }
    const saved = state.runs.find((item) => path === `${root}/document-compilations/${item.id}`)
    if (saved) return route.fulfill({ json: saved })
    const downloadRun = state.runs.find((item) => path.startsWith(`${root}/document-compilations/${item.id}/download/`))
    if (downloadRun) {
      state.downloads.push(path)
      const kind = path.split('/').pop()
      return route.fulfill({
        contentType: kind === 'report' ? 'application/json' : 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        body: kind === 'report' ? JSON.stringify(downloadRun.report) : model,
      })
    }
    return route.fulfill({ status: 404, json: { detail: 'Risorsa di test non prevista' } })
  })
  return state
}

async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= document.documentElement.clientWidth)).toBe(true)
  for (const control of await page.locator('.docx-workspace button:visible, .template-format select').all()) {
    expect(await control.evaluate((el) => el.scrollWidth <= el.clientWidth + 1)).toBe(true)
  }
}

test('Word upload, compilation, report, downloads and persisted history work inside Template', async ({ page }, testInfo) => {
  const errors: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  const state = await fixture(page)
  await page.goto('/projects/docx-test')
  await page.getByRole('link', { name: /Template/ }).click()
  await expect(page.getByLabel('Formato template')).toHaveValue('docx')
  await expect(page.getByRole('button', { name: 'Compila Word' })).toBeDisabled()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-empty.png`, fullPage: true })
  await page.getByLabel('Carica modello DOCX').setInputFiles(modelPath)
  await page.getByLabel(/Indicazioni per la compilazione/).fill('Partecipazione singola. Non compilare le firme.')
  expect(state.generations).toBe(0)
  await page.getByRole('button', { name: 'Compila Word' }).click()
  await expect(page.getByText('Ragione sociale', { exact: true })).toBeVisible()
  expect(state.generations).toBe(1)
  expect(state.payload).toContain('name="file"; filename="domanda-partecipazione.docx"')
  expect(state.payload).toContain('Partecipazione singola. Non compilare le firme.')
  await expect(page.getByText('Mapi Ingegneria S.r.l.', { exact: true })).toBeVisible()
  await page.getByText('Ragione sociale', { exact: true }).click()
  await expect(page.getByText('Denominazione: Mapi Ingegneria S.r.l.', { exact: true })).toBeVisible()
  await expect(page.getByText(/visura-simulata.pdf/)).toContainText('Frammento 2')
  await expect(page.getByText(/visura-simulata.pdf/)).not.toContainText('Pagina')
  await page.getByText('Avvisi e copertura fonti (2)').click()
  await expect(page.getByText(/Contesto parziale/, { exact: false }).first()).toBeVisible()
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-report.png`, fullPage: true })

  for (const [label, filename] of [
    ['Scarica Word compilato', 'domanda-partecipazione-bozza.docx'],
    ['Report JSON', 'report.json'],
    ['Modello originale', 'domanda-partecipazione.docx'],
  ]) {
    const downloading = page.waitForEvent('download')
    await page.getByRole('button', { name: label, exact: true }).click()
    const downloaded = await downloading
    expect(downloaded.suggestedFilename()).toBe(filename)
    const stream = await downloaded.createReadStream()
    const chunks = []
    for await (const chunk of stream!) chunks.push(Buffer.from(chunk))
    const bytes = Buffer.concat(chunks)
    if (filename.endsWith('.json')) expect(JSON.parse(bytes.toString()).ready_for_submission).toBe(false)
    else expect(bytes.subarray(0, 2).toString()).toBe('PK')
  }

  await page.reload()
  await expect(page.getByText('Ragione sociale', { exact: true })).not.toBeVisible()
  await page.getByRole('tab', { name: /Compilazioni salvate/ }).click()
  await expect(page.getByText('Ragione sociale', { exact: true })).toBeVisible()
  expect(state.generations).toBe(1)
  await page.getByRole('button', { name: 'Riutilizza modello' }).click()
  await expect(page.getByLabel(/Indicazioni per la compilazione/)).toHaveValue(state.runs[0].report.instructions)
  await page.getByRole('button', { name: 'Compila Word' }).click()
  await expect(page.getByLabel('Compilazioni salvate', { exact: true }).locator('option')).toHaveCount(2)
  await page.getByLabel('Compilazioni salvate', { exact: true }).selectOption('run-1')
  await expect(page.getByText('Ragione sociale', { exact: true })).toBeVisible()
  expect(state.generations).toBe(2)
  await page.getByRole('button', { name: /Residenze universitarie di Catanzaro/ }).click()
  await expect(page.getByRole('link', { name: /Template/ })).toContainText('2 compilazioni Word')
  expect(errors).toEqual([])
})

test('model and instructions survive generation failure and prevent accidental navigation', async ({ page }, testInfo) => {
  const state = await fixture(page)
  state.fail = true
  await page.goto(url)
  await page.getByLabel('Carica modello DOCX').setInputFiles(modelPath)
  await page.getByLabel(/Indicazioni per la compilazione/).fill('Indicazioni da conservare')
  page.once('dialog', (dialog) => dialog.dismiss())
  await page.getByLabel('Formato template').selectOption('text')
  await expect(page.getByLabel('Formato template')).toHaveValue('docx')
  page.once('dialog', (dialog) => dialog.dismiss())
  await page.getByRole('button', { name: /Dati del progetto/ }).click()
  await expect(page.getByLabel(/Indicazioni per la compilazione/)).toHaveValue('Indicazioni da conservare')
  await page.getByRole('button', { name: 'Compila Word' }).click()
  await expect(page.getByRole('alert')).toHaveText('Risposta del modello non valida')
  await expect(page.getByText('domanda-partecipazione.docx', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Compila Word' })).toBeEnabled()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-error.png`, fullPage: true })
  state.fail = false
  await page.getByRole('button', { name: 'Compila Word' }).click()
  await expect(page.getByRole('button', { name: 'Scarica Word compilato' })).toBeVisible()
})

test('long field values and filenames stay contained on a narrow screen', async ({ page }, testInfo) => {
  const state = await fixture(page, true)
  state.runs[0].template_name = `${'modello'.repeat(20)}.docx`
  state.runs[0].report.fields[0].written_value = 'valore'.repeat(100)
  state.runs[0].report.fields[0].evidence[0].quote = 'citazione'.repeat(100)
  await page.setViewportSize({ width: 360, height: 800 })
  await page.goto(url)
  await page.getByRole('tab', { name: /Compilazioni salvate/ }).click()
  await page.getByText('Ragione sociale', { exact: true }).click()
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-long.png`, fullPage: true })
})

test('mixed paragraph and cell reports expose locations and unsupported controls', async ({ page }, testInfo) => {
  const state = await fixture(page, true)
  const report = state.runs[0].report
  report.schema_version = 2
  report.prompt_version = 'docx-fields-v2'
  report.fields[0].cell_id = 'p0.s0'
  report.fields[0].location = { kind: 'paragraph', paragraph: 1, slot: 1, placeholder: '{{ragione_sociale}}' }
  report.unclassified_fields = ['p3.s0', ...report.unclassified_cells]
  report.unsupported_locations = [{ paragraph: 9, reason: 'Controllo Word non modificato' }]
  state.runs[0].template_name = 'modulo-misto.docx'
  await page.goto(url)
  await page.getByRole('tab', { name: /Compilazioni salvate/ }).click()
  await page.getByText('Ragione sociale', { exact: true }).click()
  await expect(page.getByText('Paragrafo 1 · Campo 1 · p0.s0')).toBeVisible()
  await page.getByText('Avvisi e copertura fonti (2)').click()
  await expect(page.getByText('Paragrafo 9: Controllo Word non modificato')).toBeVisible()
  await expect(page.getByText(/Elementi non classificati, non necessariamente campi mancanti:/)).toContainText('p3.s0')
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-paragraphs.png`, fullPage: true })
})

test('v3 reports distinguish user data, blocked fields and automatic corrections', async ({ page }, testInfo) => {
  const state = await fixture(page, true)
  const report = state.runs[0].report
  report.schema_version = 3
  const inserted = report.fields[0]
  inserted.evidence[0] = {
    ...inserted.evidence[0], source_id: 'user:instructions', origin: 'user', scope: 'user',
    document_id: null, fragment: null, source_kind: 'user_instructions',
    source_name: 'Indicazioni della compilazione',
  }
  inserted.repair = {
    status: 'corrected', attempted: true, message: 'Proposta corretta dopo i controlli tecnici; bozza da revisionare',
    initial_proposal: { value: 'Mapi', validation_notes: ['Citazione iniziale non valida'], rejected_evidence: [] },
  }
  const blocked = report.fields[1]
  blocked.status = 'needs_review'
  blocked.validation_notes = ['La citazione non compare nella fonte indicata']
  blocked.rejected_evidence = [{ source_id: 'project:999', quote: 'Dato non fornito', reason: 'Fonte non fornita' }]
  blocked.repair = {
    status: 'unresolved', attempted: true, message: 'Proposta ancora bloccata; campo lasciato vuoto',
    initial_proposal: { value: null, validation_notes: ['Fonte assente'], rejected_evidence: blocked.rejected_evidence },
  }
  await page.goto(url)
  await page.getByRole('tab', { name: /Compilazioni salvate/ }).click()
  await page.getByText('Ragione sociale', { exact: true }).click()
  await expect(page.getByText('Correzione automatica applicata', { exact: true })).toBeVisible()
  await expect(page.getByText("Indicazioni della compilazione · Dato dichiarato dall'utente", { exact: true })).toBeVisible()
  await expect(page.getByText(/Frammento null/)).not.toBeVisible()
  await page.getByText('Codice fiscale del firmatario', { exact: true }).click()
  await expect(page.getByText('Riferimenti rifiutati', { exact: true })).toBeVisible()
  await expect(page.getByText('Correzione non applicata', { exact: true })).toBeVisible()
  await expect(page.getByText('Bloccato', { exact: true })).toHaveCount(2)
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-repair.png`, fullPage: true })
})

test('three models stay separate and resetting an unsuccessful attempt preserves saved compilations', async ({ page }, testInfo) => {
  const state = await fixture(page, true)
  for (const [id, name] of [['run-2', 'dichiarazione-requisiti.docx'], ['run-3', 'offerta-tecnica.docx'], ['run-4', state.runs[0].template_name]]) {
    const saved = documentCompilationFixture('docx-test', id)
    saved.template_name = name
    state.runs.push(saved)
  }
  await page.goto(url)
  await expect(page.getByRole('tab', { name: 'Nuova compilazione' })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByRole('button', { name: 'Scarica Word compilato' })).not.toBeVisible()
  await page.getByRole('tab', { name: /Compilazioni salvate/ }).click()
  await expect(page.getByLabel('Compilazioni salvate', { exact: true }).locator('optgroup')).toHaveCount(3)
  await expect(page.getByLabel('Compilazioni salvate', { exact: true }).locator('option')).toHaveCount(4)
  for (const saved of state.runs) {
    await page.getByLabel('Compilazioni salvate', { exact: true }).selectOption(saved.id)
    await expect(page.getByRole('heading', { name: saved.template_name, exact: true })).toBeVisible()
    const downloading = page.waitForEvent('download')
    await page.getByRole('button', { name: 'Scarica Word compilato' }).click()
    const file = await downloading
    expect(file.suggestedFilename()).toBe(saved.template_name.replace('.docx', '-bozza.docx'))
    expect(state.downloads.at(-1)).toContain(`/${saved.id}/download/docx`)
  }
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-history.png`, fullPage: true })
  await page.getByRole('button', { name: 'Riutilizza modello' }).click()
  await expect(page.getByRole('tab', { name: /Nuova compilazione/ })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByRole('button', { name: 'Scarica Word compilato' })).not.toBeVisible()
  state.fail = true
  await page.getByRole('button', { name: 'Compila Word' }).click()
  await expect(page.getByRole('alert')).toHaveText('Risposta del modello non valida')
  await expect(page.getByRole('button', { name: 'Scarica Word compilato' })).not.toBeVisible()
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: 'Reimposta compilazione' }).click()
  await expect(page.getByRole('alert')).not.toBeVisible()
  await expect(page.getByLabel(/Indicazioni per la compilazione/)).toHaveValue('')
  await expect(page.getByRole('button', { name: 'Compila Word' })).toBeDisabled()
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-docx-reset.png`, fullPage: true })
  await page.getByRole('tab', { name: /Compilazioni salvate/ }).click()
  await expect(page.getByLabel('Compilazioni salvate', { exact: true }).locator('option')).toHaveCount(4)
  await expect(page.getByRole('button', { name: 'Scarica Word compilato' })).toBeEnabled()
  expect(state.generations).toBe(1)
})
