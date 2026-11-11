import { expect, test } from '@playwright/test'
import type { CompilationSession, ConversationTurnData } from '../src/types'

for (const motion of ['reduce', 'no-preference'] as const) {
  test(`compilation follow-up shows one stable activity then a concise answer: ${motion}`, async ({ page }) => {
    await page.emulateMedia({ reducedMotion: motion })
    const root = '/api/projects/continuation'
    const summary = 'Ho trovato i dati societari. Confermi la partecipazione?'
    const final = 'Conferme registrate. Lascio il sottoscrittore in bianco.'
    const state: CompilationSession = {
      id: 'session-1', engine: 'global', project_id: 'continuation', form_id: 42,
      original_file_id: 42, conversation_id: 'chat-1', template_name: 'modulo.docx', version: 3,
      status: 'WAITING_FOR_USER', created_at: '', updated_at: '', lease_until: null,
      last_error: null, last_generation: null, fields: [], open_issues: [],
      summary: { total: 2, pending: 0, resolved: 0, missing: 0, ambiguous: 0,
        conflicting: 0, not_applicable: 0, user_provided: 0 },
      chat: { enabled: true, auto_continue: false, paused: false, question: null,
        analyzed: 2, verified: 0, user_provided: 0, remaining_questions: 1,
        steps_used: 1, max_steps: 1 },
      global_compilation: { phase: 'REVIEW', attempts: 1, candidate_count: 2, proposal_count: 1,
        omitted: 1, rejected: 0, report_url: '/audit', fields: [], conditions: [],
        dialogue: { phase: 'READY', message: summary } },
    }
    const turns: ConversationTurnData[] = [{ id: 1, question: 'Compila', answer: summary,
      generation_status: 'direct', model: 'simulato', total_tokens: 1, notice: null,
      citations: [], evidence: [], missing_information: [],
      compilation: { session_id: state.id, action: 'start' } }]
    let delayRead = false
    let releaseRead!: () => void
    let releaseUpdate!: () => void
    const readGate = new Promise<void>((resolve) => { releaseRead = resolve })
    const updateGate = new Promise<void>((resolve) => { releaseUpdate = resolve })
    let updates = 0
    await page.route('**/api/**', async (route) => {
      const request = route.request(), path = new URL(request.url()).pathname
      if (path === root) return route.fulfill({ json: {
        id: 'continuation', title: 'Test dialogo', description: '', status: 'Bozza', status_tone: 'info',
        updated_label: '', source_count: 0, model_count: 1, instructions: '', call_fact_count: 0,
        missing_fact_count: 0, files: [{ id: 42, name: 'modulo.docx', kind: 'form', status: 'Indicizzato', metadata: '' }],
        knowledge_sources: [], conversations: [],
      } })
      if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
      if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
      if (path === `${root}/conversations/chat-1`) return route.fulfill({ json: {
        id: 'chat-1', project_id: 'continuation', title: 'Dialogo', target: 'chat', metadata: '', turns,
      } })
      if (path === `${root}/compilation-sessions`) return route.fulfill({ json: [state] })
      if (path === `${root}/compilation-sessions/session-1`) {
        if (delayRead) await readGate
        return route.fulfill({ json: state })
      }
      if (path.endsWith('/session-1/resolve')) {
        updates++
        expect(request.postDataJSON().version).toBe(4)
        await updateGate
        state.version = 6
        state.chat!.auto_continue = false
        state.global_compilation!.dialogue = { phase: 'READY', message: final, user_turns: 1 }
        turns.at(-1)!.answer = final
        return route.fulfill({ json: state })
      }
      if (path === `${root}/answer`) {
        expect(request.postDataJSON().compilation_version).toBe(3)
        state.version = 4
        delayRead = true
        state.chat!.auto_continue = true
        state.global_compilation!.dialogue = { phase: 'PENDING', message: summary, user_turns: 1 }
        const turn: ConversationTurnData = { ...turns[0], id: 2,
          question: request.postDataJSON().question,
          answer: 'Ho registrato le indicazioni univoche. Continuo con i punti rimasti aperti.',
          compilation: { session_id: state.id, action: 'updated' } }
        turns.push(turn)
        return route.fulfill({ json: { ...turn, conversation_id: 'chat-1', turn_id: turn.id } })
      }
      return route.fulfill({ json: [] })
    })
    await page.goto('/projects/continuation/conversations/chat-1')
    await expect(page.getByText(summary)).toBeVisible()
    await page.evaluate(() => {
      const snapshots: string[] = []
      Object.assign(window, { continuationSnapshots: snapshots })
      new MutationObserver(() => {
        const turns = document.querySelectorAll('.chat-turn')
        if (turns.length === 2) snapshots.push(turns[1].querySelector('.grounded-answer')?.textContent ?? '')
      }).observe(document.body, { childList: true, subtree: true, characterData: true })
    })
    await page.getByRole('textbox', { name: 'Messaggio per l’assistente' }).fill('1 sì 2 sì e 3 lascia in bianco')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    const current = page.locator('.chat-turn').last().locator('.grounded-answer')
    await expect(current.getByRole('status')).toHaveText('Verifica dei dati…')
    await expect(current.getByRole('status')).toHaveCount(1)
    releaseRead()
    await expect.poll(() => updates).toBe(1)
    await expect(current).not.toContainText('Analizzo')
    releaseUpdate()
    await expect(current).toContainText(final)
    await expect(current.getByRole('status')).toHaveCount(0)
    const snapshots = await page.evaluate(() => Reflect.get(window, 'continuationSnapshots') as string[])
    expect(snapshots.some((text) => text.includes('Ho registrato le indicazioni univoche')
      || text.includes('Analizzo l’intero') || text.includes(summary))).toBe(false)
    await page.reload()
    await expect(page.getByText(final)).toBeVisible()
    await expect(page.getByText(summary)).toBeVisible()
    expect(state.global_compilation!.attempts).toBe(1)
    expect(state.last_generation).toBeNull()
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true)
  })
}
