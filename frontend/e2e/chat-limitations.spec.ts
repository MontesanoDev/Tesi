import { expect, test } from '@playwright/test'
import type { ConversationTurnData, Evidence, GenerationStatus } from '../src/types'

for (const scenario of ['form', 'source', 'no_evidence'] as const) {
  test(`chat keeps limitations conversational without an automatic checklist: ${scenario}`, async ({ page }) => {
    const root = '/api/projects/chat-limitations'
    const message = scenario === 'form'
      ? 'Il modulo raccoglie i dati del partecipante. Il riassunto riguarda le parti consultate [1].'
      : 'Non trovo nelle fonti informazioni sufficienti per confermare la data richiesta.'
    const evidence: Evidence[] = scenario === 'no_evidence' ? [] : [{
      chunk_id: 1, file_id: 1, source_name: 'documento.txt', chunk_index: 0,
      excerpt: 'Contenuto consultato', relevance: 1, role: scenario,
    }]
    const turns: ConversationTurnData[] = []
    await page.route('**/api/**', async (route) => {
      const path = new URL(route.request().url()).pathname
      if (path === root) return route.fulfill({ json: {
        id: 'chat-limitations', title: 'Test chat', description: 'Progetto di prova',
        status: 'Bozza', status_tone: 'info', updated_label: '', source_count: 0, model_count: 0,
        instructions: '', call_fact_count: 0, missing_fact_count: 0,
        files: [], knowledge_sources: [], conversations: [],
      } })
      if (path === '/api/settings/ai') return route.fulfill({ json: { profiles: [], default_profile_id: null } })
      if (path.endsWith('/ai-model')) return route.fulfill({ json: { profile_id: null, effective_profile: null } })
      if (path === `${root}/conversations/chat-1`) return route.fulfill({ json: {
        id: 'chat-1', project_id: 'chat-limitations', title: 'Chat', metadata: '', target: 'chat', turns,
      } })
      if (path === `${root}/answer`) {
        const body = route.request().postDataJSON()
        const turn: ConversationTurnData = {
          id: 1, question: body.question, answer: message, citations: evidence.length ? [1] : [],
          missing_information: ['Dichiarazioni non recuperate nel vecchio riepilogo'], evidence,
          generation_status: (scenario === 'no_evidence' ? 'no_evidence' : 'completed') as GenerationStatus,
          model: 'simulato', total_tokens: 1, notice: null,
        }
        turns.push(turn)
        return route.fulfill({ json: { ...turn, conversation_id: 'chat-1', turn_id: turn.id } })
      }
      return route.fulfill({ json: [] })
    })
    await page.goto('/projects/chat-limitations')
    await page.getByRole('textbox', { name: 'Messaggio per l’assistente' }).fill('Riassumi il documento')
    await page.getByRole('button', { name: 'Invia', exact: true }).click()
    await expect(page.getByText(message)).toBeVisible()
    await expect(page.getByText('Informazioni mancanti')).toHaveCount(0)
    await expect(page.getByText('Dichiarazioni non recuperate nel vecchio riepilogo')).toHaveCount(0)
    await expect(page).toHaveURL(/conversations\/chat-1$/)
    await page.reload()
    await expect(page.getByText(message)).toBeVisible()
    await expect(page.locator('.missing-information')).toHaveCount(0)
    if (evidence.length) {
      await page.getByText('Evidenze recuperate', { exact: true }).click()
      await expect(page.getByText('Contenuto consultato')).toBeVisible()
      await expect(page.getByText(scenario === 'form' ? 'Modulo' : 'Fonte', { exact: true })).toBeVisible()
    }
    expect(turns[0].missing_information).toHaveLength(1)
  })
}
