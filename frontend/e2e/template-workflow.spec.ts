import { expect, test, type Page } from '@playwright/test'

async function fixture(page: Page, existing = false) {
  const projectId = 'template-test'
  const model = {
    id: `${projectId}--template`, kind: 'template', scope: 'project', title: 'Template',
    filename: 'template.md', status: 'Bozza', byte_size: 300, version: 2,
    updated_at: '', editable: true, chunk_count: 2,
    content: '---\nartifact: template\n---\n\n# Proposta di intervento\n\n## Obiettivi\n\n[TODO: descrivere gli obiettivi]\n\n## Quadro economico\n\n| Voce | Importo |\n| --- | --- |\n| Lavori | Da compilare |',
  }
  const compiled = '---\nartifact: output_draft\nstatus: pending_review\n---\n\n# Riqualificazione edificio scolastico\n\n## Descrizione intervento\n\nAdeguamento degli spazi didattici e miglioramento delle condizioni di accessibilita [CF:cf-01].\n\n## Quadro economico\n\n| Voce | Importo |\n| --- | --- |\n| Lavori | [TODO: importo richiesto] |\n| Progettazione | [TODO: oneri tecnici] |\n\n## Informazioni mancanti\n\n- Importo richiesto\n- Oneri tecnici\n\n## Provenienza\n\n- [CF:cf-01] Obiettivo - bando.pdf, frammento 12';
  const output = { ...model, id: `${projectId}--draft`, kind: 'output_draft', title: 'Draft',
    filename: 'draft.md', status: existing ? 'Da verificare' : 'Da generare',
    content: existing ? compiled : '# Draft\n\nGenerare dal template.', chunk_count: 0,
  }
  const facts = { ...model, id: `${projectId}--call-facts`, kind: 'call_facts',
    title: 'Call Facts', filename: 'call-facts.md', status: 'Verificato', content: '# Call Facts',
  }
  const projectFacts = { ...model, id: `${projectId}--project-facts`, kind: 'project_facts',
    title: 'Project Facts', filename: 'project-facts.md', content: '# Dati del progetto',
  }
  const state = { model, output, generations: 0, failure: false }
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    const root = `/api/projects/${projectId}`
    if (path === root) return route.fulfill({ json: {
      id: projectId, title: 'Riqualificazione edilizia scolastica', description: 'Candidatura del Comune',
      status: 'In analisi', status_tone: 'info', updated_label: 'Ora', source_count: 0,
      model_count: 1, instructions: '', call_fact_count: 1, missing_fact_count: 0,
      files: [], knowledge_sources: [], conversations: [],
    } })
    if (path === `${root}/artifacts`) return route.fulfill({ json: [facts, projectFacts, model, output] })
    if (path === `${root}/document-compilations`) return route.fulfill({ json: [] })
    const artifact = [model, output, facts, projectFacts].find((item) => path === `${root}/artifacts/${item.id}`)
    if (artifact) {
      if (route.request().method() === 'PUT') {
        artifact.content = route.request().postDataJSON().content
        artifact.version += 1
        artifact.status = 'Bozza aggiornata'
      }
      return route.fulfill({ json: artifact })
    }
    if (path === `${root}/draft/generate`) {
      if (state.failure) return route.fulfill({ status: 502, json: { detail: 'Servizio di generazione non disponibile' } })
      state.generations += 1
      output.content = compiled
      output.status = 'Da verificare'
      output.version += 1
      return route.fulfill({ json: { artifact: output, available_fact_count: 1, verified_fact_count: 0, used_fact_count: 1,
        missing_information: ['Importo richiesto', 'Oneri tecnici'], model: 'mock', total_tokens: 1,
      } })
    }
    if (path === `${root}/call-facts`) return route.fulfill({ json: {
      artifact: facts, facts: [], missing_information: [], pending_count: 0, verified_count: 0, discarded_count: 0,
    } })
    return route.fulfill({ status: 404, json: { detail: 'Unmocked request' } })
  })
  return state
}

async function noOverflow(page: Page) {
  expect(await page.evaluate(() => document.documentElement.scrollWidth
    <= document.documentElement.clientWidth)).toBe(true)
  for (const button of await page.locator('.template-workspace button:visible').all()) {
    expect(await button.evaluate((el) => el.scrollWidth <= el.clientWidth + 1)).toBe(true)
  }
}

test('Template imports, generates, edits, persists and exports in one workspace', async ({ page }, testInfo) => {
  const state = await fixture(page)
  await page.goto('/projects/template-test')
  await expect(page.getByRole('link', { name: /Draft/ })).toHaveCount(0)
  await page.getByRole('link', { name: /Template/ }).click()
  await page.getByLabel('Formato template').selectOption('text')
  await expect(page.getByRole('heading', { name: 'Proposta di intervento' })).toBeVisible()
  await expect(page.getByRole('table')).toBeVisible()
  await expect(page.getByText('artifact: template')).toHaveCount(0)
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-template-model.png`, fullPage: true })

  await page.getByLabel('Importa modello Markdown o TXT').setInputFiles({
    name: 'nuovo-modello.txt', mimeType: 'text/plain', buffer: Buffer.from('# Modello importato\n\n## Descrizione\n\n[TODO: obiettivi]'),
  })
  await expect(page.getByRole('textbox')).toHaveValue(/Modello importato/)
  await expect(page.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
  expect(state.model.content).toContain('Proposta di intervento')
  await page.getByRole('button', { name: 'Salva modello' }).click()
  await expect(page.getByText('Modello salvato.', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Genera compilazione' }).click()
  const preview = page.getByRole('article', { name: 'Anteprima compilazione' })
  await expect(preview.getByRole('heading', { name: 'Riqualificazione edificio scolastico' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Template', exact: true })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Compilazione' })).toHaveAttribute('aria-selected', 'true')
  await expect(preview.getByRole('heading', { name: 'Informazioni mancanti' })).toBeVisible()
  expect(state.generations).toBe(1)
  await noOverflow(page)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-template-compilation.png`, fullPage: true })

  await page.getByRole('button', { name: 'Modifica testo' }).click()
  const edited = `${state.output.content}\n\nNota revisionata dal progettista.`
  await page.getByRole('textbox').fill(edited)
  await expect(page.getByRole('button', { name: 'Scarica Markdown' })).toBeDisabled()
  await page.getByRole('button', { name: 'Salva compilazione' }).click()
  await expect(page.getByText('Compilazione salvata.', { exact: true })).toBeVisible()
  expect(state.output.content).toBe(edited)
  expect(state.model.content).toContain('Modello importato')
  const downloaded = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Scarica Markdown' }).click()
  const download = await downloaded
  expect(download.suggestedFilename()).toBe('template-compilato.md')
  const stream = await download.createReadStream()
  const chunks: Buffer[] = []
  for await (const chunk of stream!) chunks.push(Buffer.from(chunk))
  expect(Buffer.concat(chunks).toString('utf-8')).toBe(edited)
  await page.reload()
  await page.getByLabel('Formato template').selectOption('text')
  await page.getByRole('tab', { name: 'Compilazione' }).click()
  await expect(preview).toContainText('Nota revisionata dal progettista.')
  expect(state.generations).toBe(1)
})

test('existing Draft links preserve output and regeneration asks before replacing it', async ({ page }) => {
  const state = await fixture(page, true)
  await page.goto('/projects/template-test/knowledge?artifact=output_draft')
  await expect(page.getByRole('tab', { name: 'Compilazione' })).toHaveAttribute('aria-selected', 'true')
  await expect(page.getByRole('heading', { name: 'Riqualificazione edificio scolastico' })).toBeVisible()
  await expect(page.getByRole('navigation', { name: 'Preparazione candidatura' }).getByRole('button', { name: /Draft/ })).toHaveCount(0)
  page.once('dialog', (dialog) => dialog.dismiss())
  await page.getByRole('button', { name: 'Rigenera compilazione' }).click()
  expect(state.generations).toBe(0)
  page.once('dialog', (dialog) => dialog.accept())
  await page.getByRole('button', { name: 'Rigenera compilazione' }).click()
  await expect(page.getByText(/Compilazione generata:/)).toBeVisible()
  expect(state.generations).toBe(1)
})

test('unsaved changes survive tabs and cancelled navigation; generation errors remain recoverable', async ({ page }) => {
  const state = await fixture(page)
  state.failure = true
  await page.goto('/projects/template-test/knowledge?artifact=template')
  await page.getByLabel('Formato template').selectOption('text')
  await page.getByRole('button', { name: 'Modifica testo' }).click()
  await page.getByRole('textbox').fill('# Modello da salvare')
  page.once('dialog', (dialog) => dialog.dismiss())
  await page.getByRole('button', { name: /Dati del progetto/ }).click()
  await expect(page.getByRole('textbox')).toHaveValue('# Modello da salvare')
  await page.getByRole('tab', { name: 'Compilazione' }).click()
  await expect(page.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
  await page.getByRole('tab', { name: /Modello/ }).click()
  await expect(page.getByRole('heading', { name: 'Modello da salvare' })).toBeVisible()
  await page.getByRole('button', { name: 'Salva modello' }).click()
  await page.getByRole('button', { name: 'Genera compilazione' }).click()
  await expect(page.getByRole('alert')).toContainText('Servizio di generazione non disponibile')
  await expect(page.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled()
  state.failure = false
  await page.getByRole('button', { name: 'Genera compilazione' }).click()
  await expect(page.getByRole('heading', { name: 'Riqualificazione edificio scolastico' })).toBeVisible()
})

test('long content stays contained on narrow screens', async ({ page }) => {
  const state = await fixture(page, true)
  state.output.content += `\n\n${'codice'.repeat(150)}\n\n| Campo | Valore |\n| --- | --- |\n| Codice | ${'riferimento'.repeat(40)} |`
  await page.setViewportSize({ width: 360, height: 800 })
  await page.goto('/projects/template-test/knowledge?artifact=output_draft')
  await expect(page.getByRole('article', { name: 'Anteprima compilazione' })).toBeVisible()
  await noOverflow(page)
})
