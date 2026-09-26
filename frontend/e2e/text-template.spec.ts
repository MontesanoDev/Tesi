import { expect, test } from '@playwright/test'

test('text templates start empty and preserve the imported model separately from output', async ({ page }, testInfo) => {
  const projectId = 'modello-testuale'
  const template = {
    id: `${projectId}--template`, kind: 'template', title: 'Template', filename: 'template.md',
    scope: 'project', status: 'Da configurare', version: 1, updated_at: '', editable: true,
    chunk_count: 0, byte_size: 0, content: '',
  }
  const output = {
    ...template, id: `${projectId}--draft`, kind: 'output_draft', title: 'Draft', filename: 'draft.md',
    status: 'Da generare', content: '# Draft',
  }
  const source = '# Modulo specifico\n\nPEC: [TODO]\n\n## Dichiarazioni\n\n[TODO: revisione]'
  let generations = 0
  await page.route('**/api/**', async (route) => {
    const path = new URL(route.request().url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
    const base = `/api/projects/${projectId}`
    if (path === base) {
      await route.fulfill({ json: {
        id: projectId, title: 'Progetto con modello caricato', description: 'Prova template testuale',
        status: 'In analisi', status_tone: 'info', updated_label: 'ora', source_count: 0,
        model_count: 0, instructions: '', call_fact_count: 0, missing_fact_count: 0,
        files: [], knowledge_sources: [], conversations: [],
      } })
    } else if (path === `${base}/artifacts`) {
      await route.fulfill({ json: [template, output] })
    } else if (path === `${base}/artifacts/${template.id}`) {
      if (route.request().method() === 'PUT') {
        template.content = route.request().postDataJSON().content
        template.version += 1
        template.status = 'Bozza aggiornata'
        template.byte_size = template.content.length
      }
      await route.fulfill({ json: template })
    } else if (path === `${base}/artifacts/${output.id}`) {
      await route.fulfill({ json: output })
    } else if (path === `${base}/document-compilations`) {
      await route.fulfill({ json: [] })
    } else if (path === `${base}/draft/generate`) {
      generations += 1
      expect(template.content).toBe(source)
      output.content = '# Modulo specifico compilato\n\nPEC: impresa@example.test [COMPANY]'
      output.status = 'Da verificare'
      output.version += 1
      await route.fulfill({ json: {
        artifact: output, available_fact_count: 0, verified_fact_count: 0, used_fact_count: 0,
        missing_information: [], model: 'test', total_tokens: 0,
      } })
    } else {
      await route.fulfill({ status: 404, json: { detail: 'Not found' } })
    }
  })

  await page.goto(`/projects/${projectId}/knowledge?artifact=template`)
  const format = page.getByLabel('Formato template')
  await expect(format).toHaveValue('docx')
  await format.selectOption('text')
  await expect(page.getByText('Nessun modello caricato')).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Template candidatura' })).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-text-template-empty.png`, fullPage: true })
  await page.getByRole('button', { name: 'Crea modello' }).click()
  await expect(page.getByRole('textbox', { name: 'Contenuto del modello' })).toHaveValue('')
  await expect(page.getByRole('button', { name: 'Salva modello' })).toBeDisabled()
  await page.getByRole('button', { name: 'Annulla modifiche' }).click()
  await expect(page.getByText('Nessun modello caricato')).toBeVisible()

  await page.getByLabel('Importa modello Markdown o TXT').setInputFiles({
    name: 'modello-specifico.md', mimeType: 'text/markdown', buffer: Buffer.from(source),
  })
  await expect(page.getByRole('textbox', { name: 'Contenuto del modello' })).toHaveValue(source)
  await expect(page.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
  await page.getByRole('button', { name: 'Salva modello' }).click()
  await expect(page.getByText('Modello salvato.', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled()

  await format.selectOption('docx')
  await format.selectOption('text')
  await expect(page.getByRole('heading', { name: 'Modulo specifico', exact: true })).toBeVisible()
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-text-template-imported.png`, fullPage: true })
  await page.getByRole('button', { name: 'Genera compilazione' }).click()
  await expect(page.getByRole('heading', { name: 'Modulo specifico compilato' })).toBeVisible()
  await page.getByRole('tab', { name: 'Modello', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Modulo specifico', exact: true })).toBeVisible()
  expect(template.content).toBe(source)
  expect(generations).toBe(1)

  await page.reload()
  await page.getByLabel('Formato template').selectOption('text')
  await expect(page.getByRole('heading', { name: 'Modulo specifico compilato' })).toBeVisible()
  await page.getByRole('tab', { name: 'Modello', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Modulo specifico', exact: true })).toBeVisible()
  const dimensions = await page.evaluate(() => ({
    width: document.documentElement.clientWidth, scroll: document.documentElement.scrollWidth,
  }))
  expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.width)
})
