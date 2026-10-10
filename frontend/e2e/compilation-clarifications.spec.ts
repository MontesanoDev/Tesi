import { expect, test } from '@playwright/test'
import type { CompilationSession, CompilationSessionField } from '../src/types'

// API/provider simulated: browser checks never mutate the local user's data.
test('checkpoint groups questions, preserves partial replies and resumes after refresh', async ({ page }) => {
  const base = '/api/projects/grouped-chat'
  const form = { id: 42, name: 'modulo.docx', kind: 'form', metadata: 'Word', status: 'Caricato' }
  const reference = { form_id: form.id, name: form.name }
  const fields: CompilationSessionField[] = ['Recapito', 'Referente', 'Data avvio', 'Denominazione'].map((label, i) => ({
    id: `t0.r${i}.c1`, candidate_id: `t0.r${i}.c1`, label, status: 'PENDING', provenance: null,
    value: null, reason: '', validation_errors: [], requirement: null, source_evidence: [], alternatives: [],
    form_evidence: { role: 'form', source_name: form.name, candidate_id: `t0.r${i}.c1` },
  }))
  let state: CompilationSession | null = null
  let steps = 0
  let paused = false
  let answered = false
  let release!: () => void
  const checkpoint = new Promise<void>((resolve) => { release = resolve })
  const turns: object[] = []
  function view() {
    if (!state) return
    state.chat = { enabled: true, auto_continue: state.status === 'CREATED' && !paused,
      paused, paused_by_user: paused, deferred: answered ? 1 : 0,
      analyzed: 4 - state.summary.pending, verified: state.summary.resolved,
      user_provided: state.summary.user_provided, remaining_questions: state.summary.missing,
      steps_used: steps, max_steps: 36,
      question: paused || state.status === 'CREATED' ? null : {
        kind: 'clarifications', field_ids: answered ? [fields[1].id] : fields.slice(0, 3).map((f) => f.id),
        message: answered ? '2. Per «Referente» serve un’indicazione univoca. Quale valore devo usare?'
          : 'Ho compilato automaticamente 1 informazione. Per continuare mi servono 3 chiarimenti:\n1. Qual è il recapito?\n2. Chi è il referente?\n3. Qual è la data di avvio?\nPuoi rispondere anche in un unico messaggio.',
      } }
  }
  await page.route('**/api/**', async (route) => {
    const request = route.request()
    const path = new URL(request.url()).pathname
    const body = request.postData() ? request.postDataJSON() : null
    if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
    if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
    if (path === base) return route.fulfill({ json: {
      id: 'grouped-chat', title: 'Prova gruppi', description: '', status: 'Bozza', status_tone: 'info',
      updated_label: '', source_count: 0, model_count: 1, instructions: '', call_fact_count: 0,
      missing_fact_count: 0, knowledge_sources: [], conversations: [], files: [form],
    } })
    if (path === `${base}/answer`) {
      let answer = 'Certo. Analizzo il modulo e verifico le informazioni disponibili.'
      let action = 'start'
      if (!state) {
        expect(body.question).toBe('me lo compili?')
        state = { id: 'group-1', project_id: 'grouped-chat', form_id: 42, original_file_id: 42,
          conversation_id: 'chat-1', template_name: form.name, status: 'CREATED', version: 1,
          created_at: '', updated_at: '', lease_until: null, last_error: null, last_generation: null, fields,
          open_issues: [], summary: { total: 4, pending: 4, resolved: 0, missing: 0,
            ambiguous: 0, conflicting: 0, not_applicable: 0, user_provided: 0 } }
      } else if (body.question === 'basta' || body.question === 'riprendi') {
        paused = body.question === 'basta'
        state.version++
        answer = paused ? 'Va bene, metto in pausa la compilazione.' : 'Riprendo la stessa compilazione.'
        action = paused ? 'paused' : 'resumed'
      } else {
        expect(body.compilation_session_id).toBe('group-1')
        expect(body.compilation_version).toBe(state.version)
        expect(body.question).toBe('1. 055123456; 2. Anna oppure Lucia; 3. salta')
        Object.assign(fields[0], { value: '055123456', status: 'USER_PROVIDED', provenance: 'USER' })
        state.version++
        state.summary.user_provided = 1
        state.summary.missing = 2
        answered = true
        answer = 'Ho registrato il recapito. Mi serve un chiarimento soltanto sul referente.'
        action = 'clarify'
      }
      view()
      const turn = { id: turns.length + 1, question: body.question, answer,
        compilation: { session_id: state.id, action }, generation_status: 'direct',
        citations: [], evidence: [], missing_information: [], notice: null,
        model: 'simulato', total_tokens: 1, form_reference: reference }
      turns.push(turn)
      return route.fulfill({ json: { ...turn, turn_id: turn.id, conversation_id: 'chat-1' } })
    }
    if (path === `${base}/conversations/chat-1`) return route.fulfill({ json: {
      id: 'chat-1', project_id: 'grouped-chat', title: 'Compilazione', metadata: '', target: 'chat',
      form_reference: reference, turns,
    } })
    if (path === `${base}/compilation-sessions`) return route.fulfill({ json: state ? [state] : [] })
    if (path.endsWith('/group-1/resolve')) {
      steps++
      expect(body).toEqual({ version: state!.version, automatic: true })
      if (steps === 1) {
        fields[0].status = fields[1].status = 'MISSING'
        state!.summary.pending = state!.summary.missing = 2
        // Despite two unresolved fields, work continues without a USER question.
      } else {
        expect(steps).toBe(2)
        await checkpoint
        fields[2].status = 'MISSING'
        Object.assign(fields[3], { status: 'RESOLVED', value: 'Aurora S.r.l.', provenance: 'SOURCE' })
        state!.summary = { ...state!.summary, pending: 0, missing: 3, resolved: 1 }
        state!.status = 'WAITING_FOR_USER'
      }
      state!.version += 2
      view()
      return route.fulfill({ json: state })
    }
    if (path.endsWith('/group-1')) return route.fulfill({ json: state })
    return route.fulfill({ json: [] })
  })
  await page.goto('/projects/grouped-chat')
  const composer = page.getByRole('textbox', { name: 'Messaggio per Mapi RAG' })
  async function send(message: string) {
    await composer.fill(message)
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
  }
  await composer.fill('@')
  await page.getByRole('option', { name: form.name }).click()
  await send('me lo compili?')
  await expect.poll(() => steps).toBe(2)
  await expect(page.getByRole('status', { name: 'Mapi sta elaborando' })).toBeVisible()
  await expect(page.locator('.compilation-question')).toHaveCount(0)
  await expect(page.getByRole('button', { name: 'Continua analisi' })).not.toBeVisible()
  release()
  await expect(page.locator('.compilation-question')).toContainText('3 chiarimenti')
  await page.reload()
  await expect(page.locator('.compilation-question')).toContainText('3 chiarimenti')
  await send('1. 055123456; 2. Anna oppure Lucia; 3. salta')
  await expect(page.locator('.compilation-question')).toContainText('Referente')
  await expect(page.locator('.compilation-question')).not.toContainText('data di avvio')
  await expect(page.locator('.compilation-question')).not.toContainText('recapito')
  expect(fields[0].provenance).toBe('USER')
  expect(fields[1].value).toBeNull()
  expect(fields[3].provenance).toBe('SOURCE')
  await send('basta')
  await expect(page.locator('.compilation-question')).toHaveCount(0)
  await page.reload()
  await expect(page.locator('.compilation-question')).toHaveCount(0)
  await send('riprendi')
  await expect(page.locator('.compilation-question')).toContainText('Referente')
  expect(steps).toBe(2)
  await expect(page.getByRole('button', { name: 'Genera DOCX' })).not.toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
})
