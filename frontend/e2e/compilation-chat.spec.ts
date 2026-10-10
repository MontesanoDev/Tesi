import { expect, test } from '@playwright/test'
import type { CompilationChatAction, CompilationSession, CompilationSessionField, ConversationTurnData } from '../src/types'

// API and AI are simulated. Neither browser project touches the user's backend data.
for (const reducedMotion of [false, true]) {
  test(`conversational compilation${reducedMotion ? ' with reduced motion' : ''}`, async ({ page }, testInfo) => {
    await page.emulateMedia({ reducedMotion: reducedMotion ? 'reduce' : 'no-preference' })
    const form = { id: 42, name: 'domanda-partecipazione.docx', kind: 'form', metadata: 'Word', status: 'Caricato' }
    const reference = { form_id: form.id, name: form.name }
    const explanation = 'Mi riferisco alla data in cui il direttore tecnico ha ottenuto l’abilitazione professionale. Se non la conosci, possiamo lasciarla da verificare e proseguire.'
    const fields: CompilationSessionField[] = ['Denominazione sociale', 'Data abilitazione direttore tecnico'].map((label, i) => ({
      id: `t0.r${i}.c1`, candidate_id: `t0.r${i}.c1`, label, status: 'PENDING', provenance: null,
      value: null, reason: '', validation_errors: [], requirement: null, source_evidence: [], alternatives: [],
      form_evidence: { role: 'form', source_name: form.name, candidate_id: `t0.r${i}.c1` },
    }))
    let state: CompilationSession | null = null
    const turns: ConversationTurnData[] = []
    let starts = 0
    let steps = 0
    let paused = false
    let deferred = false
    let release!: () => void
    const firstStep = new Promise<void>((resolve) => { release = resolve })
    const base = '/api/projects/compilation-chat'
    function view() {
      if (!state) return
      state.chat = { enabled: true, auto_continue: state.status === 'CREATED' && !paused,
        paused, paused_by_user: paused, deferred: deferred ? 1 : 0,
        analyzed: state.summary.total - state.summary.pending, verified: state.summary.resolved,
        user_provided: state.summary.user_provided, remaining_questions: state.summary.missing,
        steps_used: steps, max_steps: 36,
        question: paused ? null : deferred ? { kind: 'deferred_summary', field_ids: [],
          message: 'La data di abilitazione resta non verificata e rinviata.' }
          : state.status === 'WAITING_FOR_USER' ? { kind: 'value', field_ids: [fields[1].id],
          message: 'Mi manca la data di abilitazione del direttore tecnico Elisa Romano. Qual è?' }
          : state.status === 'READY' ? { kind: 'generate', field_ids: [], message: 'Vuoi che generi il DOCX?' } : null }
    }
    await page.route('**/api/**', async (route) => {
      const request = route.request()
      const path = new URL(request.url()).pathname
      const body = request.postData() ? request.postDataJSON() : null
      if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
      if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
      if (path === base) return route.fulfill({ json: {
        id: 'compilation-chat', title: 'Candidatura di prova', description: 'Compilazione nella conversazione',
        status: 'Bozza', status_tone: 'info', updated_label: '', source_count: 0, model_count: 1,
        instructions: '', call_fact_count: 0, missing_fact_count: 0, knowledge_sources: [], conversations: [],
        files: [form, { ...form, id: 43, name: 'fonte.txt', kind: 'source' }],
      } })
      if (path === `${base}/answer`) {
        expect(body.document_id).toBe(42)
        let answer = 'Il modulo richiede dati aziendali e del direttore tecnico.'
        let compilation: CompilationChatAction | null = null
        if (body.question === 'me lo compili?') {
          starts++
          state ??= { id: 'session-1', project_id: 'compilation-chat', form_id: 42, original_file_id: 42,
            conversation_id: 'chat-1', template_name: form.name, status: 'CREATED', version: 1,
            created_at: '', updated_at: '', lease_until: null, last_error: null, last_generation: null, fields,
            open_issues: fields.map((f) => ({ field_id: f.id, label: f.label, status: f.status, reason: '', validation_errors: [] })),
            summary: { total: 2, pending: 2, resolved: 0, missing: 0, ambiguous: 0, conflicting: 0, not_applicable: 0, user_provided: 0 } }
          view()
          compilation = { session_id: 'session-1', action: 'start' }
          answer = 'Certo. Analizzo il modulo e verifico le informazioni disponibili.'
        } else if (body.question === 'spiegati meglio') {
          expect(body.compilation_session_id).toBe('session-1')
          answer = explanation
        } else if (body.question === 'sì, genera la bozza') {
          expect(body.compilation_version).toBe(state!.version)
          expect(state!.status).toBe('READY')
          state!.last_generation = { id: 'run-1', project_id: 'compilation-chat', template_name: form.name, created_at: '',
            status: 'needs_review', session_version: state!.version, downloads: { docx: '/download', report: '/report', template: '/template' } }
          state!.status = 'GENERATED'
          state!.version++
          view()
          compilation = { session_id: 'session-1', action: 'generated' }
          answer = 'Ho preparato la bozza. Puoi scaricare il documento e verificarlo.'
        } else if (['salta', 'non lo so', 'basta', 'riprendi'].includes(body.question)) {
          expect(body.compilation_session_id).toBe('session-1')
          state!.version++
          if (body.question === 'basta') paused = true
          else if (body.question === 'riprendi') { paused = false; deferred = false }
          else deferred = true
          view()
          compilation = { session_id: 'session-1', action: paused ? 'paused'
            : body.question === 'riprendi' ? 'resumed' : 'deferred' }
          answer = paused ? 'Va bene, metto in pausa la compilazione.'
            : body.question === 'riprendi' ? 'Riprendo la stessa compilazione.'
              : 'La lascio non verificata e continuo.'
        } else if (body.question === 'Forse 2014 oppure 2015') {
          expect(body.compilation_session_id).toBe('session-1')
          expect(body.compilation_version).toBe(state!.version)
          state!.version++
          state!.chat!.question!.message = 'Non ho modificato i valori. Qual è la data completa da usare?'
          compilation = { session_id: 'session-1', action: 'clarify' }
          answer = 'Ho bisogno di una data univoca.'
        } else if (body.question === '12 giugno 2014') {
          expect(body.compilation_version).toBe(state!.version)
          Object.assign(fields[1], { value: '12/06/2014', provenance: 'USER', status: 'USER_PROVIDED', reason: 'Indicazione USER: 12 giugno 2014' })
          Object.assign(state!, { status: 'READY', version: state!.version + 1, open_issues: [],
            summary: { ...state!.summary, missing: 0, user_provided: 1 } })
          view()
          compilation = { session_id: 'session-1', action: 'updated' }
          answer = 'Ho registrato la tua indicazione.'
        } else expect(body.question).toBe('riassumilo')
        const turn: ConversationTurnData = { id: turns.length + 1, question: body.question, answer, compilation,
          generation_status: compilation ? 'direct' : 'completed', citations: [], evidence: [], missing_information: [], notice: null,
          model: 'simulato', total_tokens: 1, form_reference: reference }
        turns.push(turn)
        return route.fulfill({ json: { ...turn, turn_id: turn.id, conversation_id: 'chat-1' } })
      }
      if (path === `${base}/conversations/chat-1`) return route.fulfill({ json: {
        id: 'chat-1', project_id: 'compilation-chat', title: 'Compilazione', metadata: '', target: 'chat',
        form_reference: reference, turns,
      } })
      if (path === `${base}/compilation-sessions`) {
        expect(request.method()).toBe('GET') // Start is routed through /answer.
        expect(new URL(request.url()).searchParams.get('conversation_id')).toBe('chat-1')
        return route.fulfill({ json: state ? [state] : [] })
      }
      if (path.endsWith('/session-1/resolve')) {
        steps++
        expect(body).toEqual({ version: state!.version, automatic: true })
        if (steps === 1) {
          await firstStep
          Object.assign(fields[0], { status: 'RESOLVED', value: 'Mapi Ingegneria S.r.l.', provenance: 'SOURCE',
            requirement: { name: fields[0].label, person_role: '', form_quote: fields[0].label },
            source_evidence: [{ role: 'source', file_id: -1, chunk_id: -1, chunk_index: 0, source_name: 'visura.txt',
              project_id: null, scope: 'global', category: 'company', quote: 'Denominazione sociale: Mapi Ingegneria S.r.l.', excerpt: '', relevance: 1 }] })
          state!.summary = { ...state!.summary, pending: 1, resolved: 1 }
        } else {
          expect(steps).toBe(2)
          Object.assign(fields[1], { status: 'MISSING', reason: 'Nessuna fonte sufficiente',
            requirement: { name: fields[1].label, person_role: '', form_quote: fields[1].label } })
          state!.status = 'WAITING_FOR_USER'
          state!.summary = { ...state!.summary, pending: 0, missing: 1 }
          state!.open_issues = [{ field_id: fields[1].id, label: fields[1].label, status: 'MISSING', reason: fields[1].reason, validation_errors: [] }]
        }
        state!.version += 2
        view()
        const turn = turns.at(-1)
        if (!state!.chat!.auto_continue && state!.chat!.question && turn?.compilation?.action === 'start') {
          turn.answer = state!.chat!.question.message
        }
        return route.fulfill({ json: state })
      }
      if (path.endsWith('/session-1/finalize')) throw new Error('La generazione deve passare dalla chat')
      if (path.endsWith('/session-1')) return route.fulfill({ json: state })
      if (path.endsWith('/download/docx')) return route.fulfill({ body: 'simulated-docx-bytes',
        contentType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
      return route.fulfill({ json: [] })
    })
    await page.goto('/projects/compilation-chat')
    const composer = page.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
    const assistantReply = page.getByRole('region', { name: 'Risposta Mapi' }).last()
    await composer.fill('@')
    await expect(page.getByRole('option')).toHaveCount(2)
    await page.getByRole('option', { name: form.name }).click()
    await expect(page.locator('.composer-mention-chip')).toContainText(form.name)
    await composer.fill('riassumilo')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByText('Il modulo richiede dati aziendali e del direttore tecnico.')).toBeVisible()
    expect(starts).toBe(0)
    await composer.fill('me lo compili?')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByText('Certo. Analizzo il modulo e verifico le informazioni disponibili.')).toBeVisible()
    const spinner = page.locator('.assistant-activity svg')
    await expect(spinner).toBeVisible()
    expect(await spinner.evaluate((element) => getComputedStyle(element).animationName)).toBe(reducedMotion ? 'none' : 'assistant-spin')
    await expect(page.getByRole('status', { name: 'Mapi sta elaborando' })).toBeVisible()
    await expect(page.locator('.compilation-message, .compilation-debug, .compilation-counts')).toHaveCount(0)
    await composer.fill('Testo scritto durante l’elaborazione')
    await expect(composer).toBeEditable()
    await expect(page.getByRole('button', { name: 'Invia', exact: true })).toBeDisabled()
    await composer.press('Enter')
    await composer.evaluate((element) => (element as HTMLTextAreaElement).form!.requestSubmit())
    expect(starts).toBe(1)
    expect(steps).toBe(1)
    await expect(composer).toHaveValue('Testo scritto durante l’elaborazione')
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-compilation-active${reducedMotion ? '-reduced' : ''}.png`, fullPage: true })
    await expect(page.getByRole('button', { name: 'Continua analisi' })).not.toBeVisible()
    release()
    await expect(page.getByText('Mi manca la data di abilitazione del direttore tecnico Elisa Romano. Qual è?')).toBeVisible()
    expect(steps).toBe(2)
    await expect(spinner).toHaveCount(0)
    await expect(composer).toHaveValue('Testo scritto durante l’elaborazione')
    await expect(page.getByRole('button', { name: 'Invia', exact: true })).toBeEnabled()
    await expect(page.getByRole('button', { name: 'Genera DOCX' })).not.toBeVisible()
    await expect(page.getByRole('button', { name: 'Genera bozza con campi irrisolti' })).not.toBeVisible()
    await expect(page.getByText('Non posso compilare', { exact: false })).not.toBeVisible()
    await page.reload()
    await expect(page.getByText('Mi manca la data di abilitazione del direttore tecnico Elisa Romano. Qual è?')).toBeVisible()
    const versionBeforeExplanation = state!.version
    await composer.fill('spiegati meglio')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(assistantReply).toContainText(explanation)
    await expect(assistantReply.getByRole('heading', { name: 'Risposta Mapi' })).toHaveCount(1)
    await expect(assistantReply.locator('details, dl')).toHaveCount(0)
    await expect(assistantReply.getByText(/Qual è\?/)).toHaveCount(0)
    const originalCompilationReply = page.getByRole('region', { name: 'Risposta Mapi' }).nth(1)
    await expect(originalCompilationReply).toContainText('Mi manca la data di abilitazione')
    await expect(page.getByText(`Compilazione · ${form.name}`, { exact: true })).toHaveCount(0)
    expect(state!.version).toBe(versionBeforeExplanation)
    expect(fields[1].value).toBeNull()
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-compilation-explanation${reducedMotion ? '-reduced' : ''}.png`, fullPage: true })
    await page.reload()
    await expect(assistantReply).toContainText(explanation)
    await expect(assistantReply.locator('details, dl')).toHaveCount(0)
    await expect(originalCompilationReply).toContainText('Mi manca la data di abilitazione')
    for (const reply of ['salta', 'non lo so']) {
      await composer.fill(reply)
      await page.getByRole('button', { name: 'Invia', exact: true }).click()
      await expect(page.getByText('La data di abilitazione resta non verificata e rinviata.')).toBeVisible()
      await expect(assistantReply).not.toContainText('Qual è?')
      expect(fields[1].value).toBeNull()
      expect(fields[1].status).toBe('MISSING')
      await composer.fill('riprendi')
      await page.getByRole('button', { name: 'Invia', exact: true }).click()
      await expect(assistantReply).toContainText('Qual è?')
    }
    await composer.fill('basta')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByText('Va bene, metto in pausa la compilazione.')).toBeVisible()
    await expect(originalCompilationReply).toContainText('Mi manca la data di abilitazione')
    await expect(page.getByRole('button', { name: 'Prosegui compilazione' })).toHaveCount(0)
    await expect(page.getByRole('button', { name: 'Riprendi compilazione' })).toHaveCount(0)
    await expect(page.locator('.assistant-activity')).toHaveCount(0)
    await expect(assistantReply.getByText(/Qual è\?/)).toHaveCount(0)
    await page.reload()
    await expect(page.getByText('Va bene, metto in pausa la compilazione.')).toBeVisible()
    await expect(originalCompilationReply).toContainText('Mi manca la data di abilitazione')
    await expect(assistantReply.getByText(/Qual è\?/)).toHaveCount(0)
    expect(steps).toBe(2)
    await composer.fill('riprendi')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(assistantReply).toContainText('Qual è?')
    await composer.fill('Forse 2014 oppure 2015')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByText('Non ho modificato i valori. Qual è la data completa da usare?')).toBeVisible()
    expect(fields[1].value).toBeNull()
    await composer.fill('12 giugno 2014')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByText('Vuoi che generi il DOCX?')).toBeVisible()
    await page.screenshot({ path: `artifacts/${testInfo.project.name}-compilation-conversational${reducedMotion ? '-reduced' : ''}.png`, fullPage: true })
    await page.reload()
    await expect(page.getByText('Vuoi che generi il DOCX?')).toBeVisible()
    await expect(assistantReply.locator('details, dl')).toHaveCount(0)
    expect(fields[1].provenance).toBe('USER')
    expect(fields[1].value).toBe('12/06/2014')
    await composer.fill('sì, genera la bozza')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByRole('button', { name: 'Scarica DOCX' })).toBeVisible()
    await expect(assistantReply).toContainText('Ho preparato la bozza.')
    await expect(assistantReply.getByRole('button')).toHaveCount(1)
    await expect(page.getByRole('button', { name: 'Genera DOCX' })).toHaveCount(0)
    const download = page.waitForEvent('download')
    await page.getByRole('button', { name: 'Scarica DOCX' }).click()
    expect((await download).suggestedFilename()).toBe('domanda-partecipazione.compilato.docx')
    expect(starts).toBe(1)
    expect(steps).toBe(2)
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  })
}

test('refresh during a persisted lease recovers through a read error without concurrent mutations', async ({ page }) => {
  const base = '/api/projects/compilation-refresh'
  const form = { id: 42, name: 'modulo.docx', kind: 'form', metadata: '', status: 'Caricato' }
  const field: CompilationSessionField = { id: 'f1', candidate_id: 'f1', label: 'Qualifica',
    status: 'PENDING', value: null, provenance: null, reason: '', validation_errors: [],
    requirement: null, source_evidence: [], alternatives: [],
    form_evidence: { role: 'form', source_name: form.name, candidate_id: 'f1' } }
  const state: CompilationSession = { id: 'session-1', project_id: 'compilation-refresh',
    conversation_id: 'chat-1', form_id: 42, original_file_id: 42, template_name: form.name,
    status: 'ANALYZING', version: 2, created_at: '', updated_at: '', last_error: null, last_generation: null,
    lease_until: new Date(Date.now() + 240000).toISOString(), fields: [field], open_issues: [],
    summary: { total: 1, pending: 1, resolved: 0, missing: 0, ambiguous: 0, conflicting: 0, not_applicable: 0, user_provided: 0 },
    chat: { enabled: true, auto_continue: false, paused: false, question: null,
      analyzed: 0, verified: 0, user_provided: 0, remaining_questions: 0, steps_used: 1, max_steps: 36 } }
  let failedReads = 0
  let mutations = 0
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    if (request.method() !== 'GET') {
      mutations++
      return route.fulfill({ status: 409, json: { detail: 'Nessuna mutazione attesa' } })
    }
    if (path === base) return route.fulfill({ json: { id: 'compilation-refresh', title: 'Progetto di prova',
      description: '', status: 'Bozza', status_tone: 'info', updated_label: '', source_count: 0, model_count: 0,
      instructions: '', call_fact_count: 0, missing_fact_count: 0, knowledge_sources: [], conversations: [], files: [form] } })
    if (path === `${base}/conversations/chat-1`) return route.fulfill({ json: { id: 'chat-1',
      project_id: 'compilation-refresh', title: 'Compilazione', metadata: '', target: 'chat', turns: [],
      form_reference: { form_id: 42, name: form.name } } })
    if (path === `${base}/compilation-sessions`) return route.fulfill({ json: [state] })
    if (path === `${base}/compilation-sessions/session-1`) {
      if (failedReads > 0) {
        failedReads--
        return route.fulfill({ status: 503, json: { detail: 'Lettura temporaneamente non disponibile' } })
      }
      return route.fulfill({ json: state })
    }
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
    return route.fulfill({ json: [] })
  })
  await page.goto('/projects/compilation-refresh/conversations/chat-1')
  await expect(page.getByRole('status', { name: 'Mapi sta elaborando' })).toBeVisible()
  await page.reload()
  await expect(page.getByRole('status', { name: 'Mapi sta elaborando' })).toBeVisible()
  await expect(page.locator('.compilation-message, .compilation-debug, .compilation-counts')).toHaveCount(0)
  const composer = page.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
  await composer.fill('Risposta conservata')
  await expect(page.getByRole('button', { name: 'Invia', exact: true })).toBeDisabled()
  failedReads = 1
  await expect(page.getByText('Impossibile aggiornare la compilazione. I dati sono conservati.')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Invia', exact: true })).toBeDisabled()
  Object.assign(field, { status: 'MISSING' })
  Object.assign(state, { status: 'WAITING_FOR_USER', version: 3, lease_until: null,
    open_issues: [{ field_id: field.id, label: field.label, status: 'MISSING', reason: '', validation_errors: [] }],
    summary: { ...state.summary, pending: 0, missing: 1 },
    chat: { ...state.chat!, question: { kind: 'value', field_ids: [field.id], message: 'Qual è la qualifica?' } } })
  await expect(page.getByText('Qual è la qualifica?', { exact: true })).toBeVisible()
  await expect(page.getByRole('alert')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Invia', exact: true })).toBeEnabled()
  await expect(composer).toHaveValue('Risposta conservata')
  await expect(page.locator('.assistant-activity')).toHaveCount(0)
  Object.assign(state, { status: 'FAILED', last_error: 'Errore interno di prova', chat: { ...state.chat!, paused: true } })
  await page.reload()
  await expect(page.getByRole('alert')).toContainText('Ho conservato il lavoro fatto finora')
  await expect(page.getByRole('button', { name: 'Prosegui compilazione' })).toHaveCount(0)
  await expect(page.locator('.compilation-message, .compilation-debug, .compilation-counts')).toHaveCount(0)
  await expect(page.locator('.assistant-activity')).toHaveCount(0)
  await expect(page.getByText('Errore interno di prova')).toHaveCount(0)
  expect(mutations).toBe(0)
})
