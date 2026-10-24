import { expect, test } from '@playwright/test'
import type { CompilationSession, ConversationTurnData } from '../src/types'

// Browser integration only: isolated, simulated API; real provider checked separately.
test('global compilation in chat, explicit partial export and refresh', async ({ page }, testInfo) => {
  await page.emulateMedia({ reducedMotion: 'reduce' })
  const base = '/api/projects/global-chat'
  const form = { id: 42, name: 'modulo.docx', kind: 'form', metadata: 'Word', status: 'Caricato' }
  const reference = { form_id: 42, name: form.name }
  const turns: ConversationTurnData[] = []
  let state: CompilationSession | null = null
  let steps = 0
  let exports = 0
  let release!: () => void
  const gate = new Promise<void>((resolve) => { release = resolve })
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const body = request.postData() ? request.postDataJSON() : null
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
    if (path === base) return route.fulfill({ json: {
      id: 'global-chat', title: 'Compilazione globale', description: 'Prova isolata', status: 'Bozza',
      status_tone: 'info', updated_label: '', source_count: 0, model_count: 1, instructions: '',
      call_fact_count: 0, missing_fact_count: 0, knowledge_sources: [], conversations: [], files: [form],
    } })
    if (path === `${base}/answer`) {
      expect(body.document_id).toBe(42)
      const compile = body.question === 'me lo compili?'
      if (compile) state ??= {
        id: 'session-1', engine: 'global', project_id: 'global-chat', form_id: 42, original_file_id: 42,
        conversation_id: 'chat-1', template_name: form.name, status: 'CREATED', version: 1,
        created_at: '', updated_at: '', lease_until: null, last_error: null, last_generation: null,
        fields: [], open_issues: [], summary: { total: 2, pending: 2, resolved: 0, missing: 0,
          ambiguous: 0, conflicting: 0, not_applicable: 0, user_provided: 0 },
        global_compilation: { phase: 'PENDING', candidate_count: 2, attempts: 0, paused: false,
          fields: [], conditions: [], proposal_count: 0, omitted: 0, rejected: 0, report_url: null },
        chat: { enabled: true, auto_continue: true, paused: false, question: null, analyzed: 0,
          verified: 0, user_provided: 0, remaining_questions: 0, steps_used: 0, max_steps: 1 },
      }
      const reply = body.question === 'Sì, partecipiamo come società'
      const generate = body.question === 'genera la bozza parziale'
      let answer = 'Il modulo richiede i dati della società.'
      if (reply) {
        expect(state).not.toBeNull()
        state!.version++
        answer = 'Ho registrato la conferma. Vuoi che generi una bozza parziale?'
        state!.global_compilation!.dialogue = { phase: 'READY', message: answer }
      }
      if (generate) {
        exports++
        state!.status = 'GENERATED'
        state!.version++
        answer = 'Ho preparato una bozza parziale. Puoi scaricarla e controllarla.'
        state!.global_compilation!.dialogue = { phase: 'READY', message: answer }
        state!.last_generation = { id: 'run-1', project_id: 'global-chat', template_name: form.name,
          created_at: '', status: 'needs_review', session_version: state!.version - 1,
          downloads: { docx: '/download', report: '/report', template: '/template' } }
      }
      const turn: ConversationTurnData = { id: turns.length + 1, question: body.question,
        answer: compile ? 'Certo. Analizzo il modulo e verifico le informazioni disponibili.'
          : answer,
        compilation: compile || reply || generate ? { session_id: 'session-1',
          action: compile ? 'start' : generate ? 'generated' : 'updated' } : null,
        generation_status: 'direct', citations: [], evidence: [], missing_information: [],
        notice: null, model: 'simulato', total_tokens: 1, form_reference: reference }
      turns.push(turn)
      return route.fulfill({ json: { ...turn, turn_id: turn.id, conversation_id: 'chat-1' } })
    }
    if (path === `${base}/conversations/chat-1`) return route.fulfill({ json: {
      id: 'chat-1', project_id: 'global-chat', title: 'Compilazione', metadata: '', target: 'chat',
      form_reference: reference, turns,
    } })
    if (path === `${base}/compilation-sessions`) {
      expect(request.method()).toBe('GET')
      return route.fulfill({ json: state ? [state] : [] })
    }
    if (path.endsWith('/session-1/resolve')) {
      steps++
      expect(steps).toBe(1)
      expect(body).toEqual({ version: 1, automatic: true })
      await gate
      state!.status = 'WAITING_FOR_USER'
      state!.version = 3
      Object.assign(state!.chat!, { auto_continue: false, analyzed: 2, steps_used: 1 })
      state!.global_compilation = { dialogue: { phase: 'READY',
        message: 'Ho trovato denominazione e recapiti nelle fonti. La partecipazione è come società?' }, phase: 'REVIEW', candidate_count: 2, attempts: 1, paused: false,
        fields: [{ candidate_id: 't0.r0.c1', label: 'Denominazione', value: 'Aurora S.r.l.',
          validation: 'REVIEW_REQUIRED', conditional: true, conditions: ['c1'], selectable: true,
          form_context: 'Se società: denominazione', form_quote: 'denominazione', issues: [],
          source_evidence: [{ role: 'source', source_name: 'visura.txt', chunk_id: -1,
            file_id: -1, chunk_index: 0, project_id: null, scope: 'global', category: 'company',
            quote: 'Denominazione: Aurora S.r.l.', excerpt: '', relevance: 1 }] }],
        conditions: [{ id: 'c1', quote: 'Se società', result: 'unknown', reason: 'La sezione è applicabile' }],
        proposal_count: 1, omitted: 1, rejected: 0, report_url: '/audit',
      }
      return route.fulfill({ json: state })
    }
    if (path.endsWith('/global-draft')) throw new Error('No manual field-selection API in chat')
    if (path.endsWith('/session-1/finalize')) throw new Error('Legacy finalizer must not run')
    if (path.endsWith('/session-1')) return route.fulfill({ json: state })
    if (path.endsWith('/download/docx')) return route.fulfill({ body: 'simulated-docx-bytes',
      contentType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' })
    if (path.endsWith('/download/report') || path.endsWith('/global-report')) return route.fulfill({ json: { test: true } })
    return route.fulfill({ json: [] })
  })
  await page.goto('/projects/global-chat')
  const composer = page.getByRole('textbox', { name: 'Messaggio per l’assistente' })
  await composer.fill('@')
  await page.getByRole('option', { name: form.name }).click()
  await composer.fill('riassumilo')
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByText('Il modulo richiede i dati della società.')).toBeVisible()
  expect(state).toBeNull()
  await composer.fill('me lo compili?')
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByRole('status', { name: 'Elaborazione in corso' }))
    .toHaveText('Analisi del documento e compilazione delle sezioni…')
  expect(exports).toBe(0)
  release()
  await expect(page.getByText('Ho trovato denominazione e recapiti nelle fonti. La partecipazione è come società?')).toBeVisible()
  await expect(page.getByRole('button', { name: 'Continua analisi' })).toHaveCount(0)
  await expect(page.getByRole('checkbox')).toHaveCount(0)
  await expect(page.getByRole('button', { name: /Scarica report/ })).toHaveCount(0)
  await expect(page.getByText(/Rivedi proposte|t0\.r0\.c1|Nessun valore utilizzabile/)).toHaveCount(0)
  await composer.fill('Sì, partecipiamo come società')
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByText('Ho registrato la conferma. Vuoi che generi una bozza parziale?')).toBeVisible()
  expect(exports).toBe(0)
  await page.reload()
  await expect(page.getByText('Ho registrato la conferma. Vuoi che generi una bozza parziale?')).toBeVisible()
  await page.getByRole('textbox', { name: 'Messaggio per l’assistente' }).fill('genera la bozza parziale')
  await page.getByRole('button', { name: 'Invia', exact: true }).click()
  await expect(page.getByRole('button', { name: 'Scarica DOCX' })).toBeVisible()
  expect(exports).toBe(1)
  const [download] = await Promise.all([page.waitForEvent('download'), page.getByRole('button', { name: 'Scarica DOCX' }).click()])
  expect(download.suggestedFilename()).toBe('modulo.compilato.docx')
  await page.reload()
  await expect(page.getByRole('button', { name: 'Scarica DOCX' })).toBeVisible()
  await expect(page.getByRole('button', { name: /Scarica report/ })).toHaveCount(0)
  expect(steps).toBe(1)
  expect(exports).toBe(1)
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  await page.screenshot({ path: testInfo.outputPath('global-review.png'), fullPage: true })
})
