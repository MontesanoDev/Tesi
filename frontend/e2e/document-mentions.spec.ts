import { expect, test } from '@playwright/test'
import type { CompilationSession, ConversationTurnData, DocumentReference } from '../src/types'

test('document mentions consult sources and preserve the pending form across reload', async ({ page }, testInfo) => {
  const root = '/api/projects/document-mentions'
  const form = { id: 42, name: 'domanda.docx', kind: 'form', metadata: 'DOCX', status: 'Indicizzato' }
  const source = { id: 43, name: 'avviso.pdf', kind: 'source', metadata: 'PDF', status: 'Indicizzato' }
  const files = [form, source]
  let reference: DocumentReference = { document_id: form.id, name: form.name, role: 'form' }
  const question = 'Mi manca la data di abilitazione. Qual è?'
  const session: CompilationSession = {
    id: 'pending-session', project_id: 'document-mentions', conversation_id: 'chat-1',
    form_id: form.id, original_file_id: form.id, template_name: form.name,
    status: 'WAITING_FOR_USER', version: 7, created_at: '', updated_at: '', lease_until: null,
    last_error: null, last_generation: null,
    summary: { total: 1, pending: 0, resolved: 0, missing: 1, ambiguous: 0, conflicting: 0,
      not_applicable: 0, user_provided: 0 },
    fields: [{ id: 'date', candidate_id: 'date', label: 'Data abilitazione', status: 'MISSING',
      value: null, provenance: null, reason: '', validation_errors: [], alternatives: [],
      form_evidence: { role: 'form', source_name: form.name, candidate_id: 'date' }, source_evidence: [] }],
    open_issues: [{ field_id: 'date', label: 'Data abilitazione', status: 'MISSING', reason: '', validation_errors: [] }],
    chat: { enabled: true, auto_continue: false, paused: false,
      question: { kind: 'value', field_ids: ['date'], message: question }, analyzed: 1, verified: 0,
      user_provided: 0, remaining_questions: 1, steps_used: 2, max_steps: 36 },
  }
  const turns: ConversationTurnData[] = [{ id: 1, question: 'Compila il modulo', answer: question,
    generation_status: 'direct', model: 'simulato', total_tokens: 1, notice: null,
    evidence: [], citations: [], missing_information: [], document_reference: reference,
    compilation: { session_id: session.id, action: 'start' } }]
  const writes: string[] = []
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null, thinking: false } })
    if (path === root) return route.fulfill({ json: {
      id: 'document-mentions', title: 'Documenti di gara', description: 'Progetto di prova', status: 'Bozza',
      status_tone: 'info', updated_label: '', source_count: 1, model_count: 1, instructions: '',
      call_fact_count: 0, missing_fact_count: 0, files, knowledge_sources: [], conversations: [],
    } })
    if (path === `${root}/conversations/chat-1`) return route.fulfill({ json: {
      id: 'chat-1', project_id: 'document-mentions', title: 'Chat', metadata: '', target: 'chat',
      document_reference: reference, turns,
    } })
    if (path === `${root}/compilation-sessions`) return route.fulfill({ json: [session] })
    if (path === `${root}/compilation-sessions/${session.id}`) return route.fulfill({ json: session })
    if (path === `${root}/answer`) {
      const body = request.postDataJSON()
      expect(body.document_id).toBe(source.id)
      expect(body.form_id).toBeUndefined()
      expect(body.compilation_session_id).toBe(session.id)
      expect(body.compilation_version).toBe(7)
      reference = { document_id: source.id, name: source.name, role: 'source' }
      const answer = body.question === 'Compilalo'
        ? 'Posso consultare questo bando. Seleziona con @ il modulo domanda.docx da compilare.'
        : 'L’avviso descrive i requisiti per partecipare alla selezione.'
      const turn: ConversationTurnData = { id: turns.length + 1, question: body.question, answer,
        generation_status: 'completed', model: 'simulato', total_tokens: 1, notice: null,
        evidence: [], citations: [], missing_information: [], document_reference: reference }
      turns.push(turn)
      return route.fulfill({ json: { ...turn, turn_id: turn.id, conversation_id: 'chat-1' } })
    }
    if (request.method() !== 'GET') writes.push(path)
    return route.fulfill({ json: [] })
  })
  await page.goto('/projects/document-mentions/conversations/chat-1')
  const add = page.getByRole('button', { name: 'Aggiungi un documento' })
  await expect(add).toBeEnabled()
  await expect.poll(() => page.evaluate(() => document.documentElement.scrollHeight <= window.innerHeight)).toBe(true)
  expect(await page.locator('.chat-thread').evaluate((element) => element.scrollHeight <= element.clientHeight)).toBe(true)
  await add.click()
  await expect(page.getByRole('group', { name: 'Moduli da compilare' })).toBeVisible()
  await expect(page.getByRole('group', { name: 'Bandi e fonti' })).toBeVisible()
  await page.getByRole('option', { name: source.name }).click()
  const input = page.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
  await input.fill('Spiegami questo bando')
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByText('L’avviso descrive i requisiti per partecipare alla selezione.')).toBeVisible()
  await expect(page.getByText(question, { exact: true })).toBeVisible()
  await page.reload()
  await expect(page.locator('.composer-mention-chip')).toContainText('@avviso.pdf')
  await expect(page.getByText(question, { exact: true })).toBeVisible()
  await input.fill('Compilalo')
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByText('Posso consultare questo bando.', { exact: false })).toBeVisible()
  expect(session.version).toBe(7)
  expect(session.fields[0].value).toBeNull()
  expect(writes).toEqual([])
  await page.getByRole('button', { name: 'Rimuovi riferimento al documento' }).click()
  await input.fill('Spiegami @dom')
  await expect(page.getByRole('option', { name: form.name })).toBeVisible()
  await expect(page.getByRole('option', { name: source.name })).toHaveCount(0)
  await input.press('Enter')
  await expect(page.locator('.composer-mention-chip')).toContainText('@domanda.docx')
  await expect(input).toHaveValue('Spiegami ')
  expect(turns).toHaveLength(3)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: `artifacts/${testInfo.project.name}-document-mentions.png`, fullPage: true })

  // Long histories and document lists must scroll independently without hiding the composer.
  for (let index = 0; index < 15; index++) {
    turns.push({ ...turns[0], id: index + 100, question: `Domanda precedente ${index + 1}`,
      answer: 'Risposta conservata nello storico della conversazione. '.repeat(8), compilation: null })
    files.push({ ...source, id: index + 100, name: `allegato-${index + 1}.pdf` })
  }
  await page.reload()
  await expect(page.locator('.chat-turn')).toHaveCount(turns.length)
  const width = page.viewportSize()!.width
  for (const height of [700, testInfo.project.name === 'mobile' ? 915 : 960]) {
    await page.setViewportSize({ width, height })
    await expect(input).toBeInViewport()
    await expect(page.getByRole('button', { name: 'Invia', exact: true })).toBeInViewport()
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollHeight <= window.innerHeight)).toBe(true)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
    await page.evaluate(() => window.scrollTo(0, 1000))
    expect(await page.evaluate(() => window.scrollY)).toBe(0)
    const thread = page.locator('.chat-thread')
    await expect.poll(() => thread.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(true)
    await thread.evaluate((element) => { element.scrollTop = 80 })
    await expect.poll(() => thread.evaluate((element) => element.scrollTop)).toBeGreaterThan(0)

    const documentsToggle = page.getByRole('button', { name: 'Documenti', exact: true })
    if (width <= 1100) {
      await documentsToggle.click()
      await expect(documentsToggle).toHaveAttribute('aria-expanded', 'true')
    }
    const context = page.locator('#workspace-context')
    await expect(context).toBeVisible()
    await expect.poll(() => context.evaluate((element) => element.scrollHeight > element.clientHeight)).toBe(true)
    await context.evaluate((element) => { element.scrollTop = 80 })
    expect(await context.evaluate((element) => element.scrollTop)).toBeGreaterThan(0)
    await expect(input).toBeInViewport()
    await expect.poll(() => page.evaluate(() => document.documentElement.scrollHeight <= window.innerHeight)).toBe(true)
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-chat-layout-${height}.png`, fullPage: true })
    if (width <= 1100) {
      await documentsToggle.click()
      await expect(context).toBeHidden()
    }
  }
})
