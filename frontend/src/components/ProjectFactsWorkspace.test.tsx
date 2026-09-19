import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { CallFactsReview, KnowledgeArtifactDetail } from '../types'
import { ProjectFactsWorkspace } from './ProjectFactsWorkspace'

vi.mock('../api', () => ({ api: {
  callFactsReview: vi.fn(), reviseCallFact: vi.fn(), updateProjectArtifact: vi.fn(), extractCallFacts: vi.fn(),
} }))

const entered: KnowledgeArtifactDetail = {
  id: 'demo--project-facts', kind: 'project_facts', scope: 'project', title: 'Project Facts',
  filename: 'project-facts.md', version: 4, byte_size: 50, updated_at: '', status: 'Bozza',
  editable: true, chunk_count: 1, content: '# Dati inseriti\n\nFirmatario: Persona demo',
}
const review: CallFactsReview = {
  artifact: { ...entered, id: 'demo--call-facts', kind: 'call_facts', title: 'Call Facts', filename: 'call-facts.md' },
  facts: [{ id: 'cf-scadenza', title: 'Scadenza', value: '21 ottobre 2026', status: 'pending',
    sources: [{ name: 'bando.pdf', fragment: 18 }] }],
  pending_count: 1, verified_count: 0, discarded_count: 0, missing_information: ['Importo richiesto'],
}

function setup() {
  const updated = vi.fn()
  const dirty = vi.fn()
  render(<ProjectFactsWorkspace projectId="demo" artifact={entered} onUpdated={updated} onDirtyChange={dirty} />)
  return { updated, dirty }
}

describe('ProjectFactsWorkspace', () => {
  afterEach(() => { cleanup(); vi.restoreAllMocks() })
  beforeEach(() => {
    vi.mocked(api.callFactsReview).mockReset().mockResolvedValue(structuredClone(review))
    vi.mocked(api.reviseCallFact).mockReset()
    vi.mocked(api.updateProjectArtifact).mockReset().mockImplementation(async (_project, _id, content) => (
      { ...entered, version: 5, content }
    ))
    vi.mocked(api.extractCallFacts).mockReset().mockResolvedValue({
      artifact: review.artifact, fact_count: 1, missing_count: 0, evidence_count: 2, model: 'mock', total_tokens: 10,
    })
  })

  it('makes existing pending facts visible without a verification action', async () => {
    setup()
    expect(await screen.findByRole('heading', { name: 'Scadenza' })).toBeVisible()
    expect(screen.getByText('bando.pdf, frammento 18')).toBeVisible()
    expect(screen.getByText('Estratto', { exact: true })).toBeVisible()
    expect(screen.queryByRole('button', { name: 'Verifica' })).not.toBeInTheDocument()
    expect(screen.queryByText('Da verificare')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Attivi 1' })).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByText('Importo richiesto')).not.toBeVisible()
    fireEvent.click(screen.getByText('Informazioni non trovate (1)'))
    expect(screen.getByText('Importo richiesto')).toBeVisible()
  })

  it('edits a fact without requiring reapproval and preserves its source', async () => {
    const changed = structuredClone(review)
    changed.facts[0].value = '22 ottobre 2026'
    changed.facts[0].origin = 'user_corrected'
    vi.mocked(api.reviseCallFact).mockResolvedValue(changed)
    setup()
    fireEvent.click(await screen.findByRole('button', { name: 'Modifica' }))
    fireEvent.change(screen.getByLabelText('Valore'), { target: { value: '22 ottobre 2026' } })
    expect(screen.getByRole('button', { name: 'Riestrai dalle fonti' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva modifica' }))
    expect(await screen.findByText('Corretto', { exact: true })).toBeVisible()
    expect(screen.getByText('22 ottobre 2026')).toBeVisible()
    expect(screen.getByText('bando.pdf, frammento 18')).toBeVisible()
    expect(api.reviseCallFact).toHaveBeenCalledWith('demo', 'cf-scadenza', {
      action: 'edit', version: 4, title: 'Scadenza', value: '22 ottobre 2026',
    })
  })

  it('retains corrections after save failure', async () => {
    vi.mocked(api.reviseCallFact).mockRejectedValue(new Error('Conflitto di versione'))
    setup()
    fireEvent.click(await screen.findByRole('button', { name: 'Modifica' }))
    fireEvent.change(screen.getByLabelText('Valore'), { target: { value: 'Correzione da conservare' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modifica' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Conflitto di versione')
    expect(screen.getByLabelText('Valore')).toHaveValue('Correzione da conservare')
  })

  it('saves entered data separately, retaining text across tabs', async () => {
    const { dirty } = setup()
    await screen.findByRole('heading', { name: 'Scadenza' })
    fireEvent.click(screen.getByRole('tab', { name: 'Dati inseriti' }))
    const textbox = screen.getByRole('textbox')
    expect(textbox).toHaveValue(entered.content)
    fireEvent.change(textbox, { target: { value: 'Firmatario: Persona scelta' } })
    fireEvent.click(screen.getByRole('tab', { name: 'Dati estratti' }))
    expect(screen.getByRole('heading', { name: 'Scadenza' })).toBeVisible()
    fireEvent.click(screen.getByRole('tab', { name: /Dati inseriti/ }))
    expect(screen.getByRole('textbox')).toHaveValue('Firmatario: Persona scelta')
    expect(dirty).toHaveBeenLastCalledWith(true)
    fireEvent.click(screen.getByRole('button', { name: 'Salva dati' }))
    await waitFor(() => expect(dirty).toHaveBeenLastCalledWith(false))
    expect(api.updateProjectArtifact).toHaveBeenCalledWith('demo', 'demo--project-facts', 'Firmatario: Persona scelta')
    expect(api.reviseCallFact).not.toHaveBeenCalled()
  })

  it('confirms reextraction and retains unsaved entered data', async () => {
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    setup()
    await screen.findByRole('heading', { name: 'Scadenza' })
    fireEvent.click(screen.getByRole('tab', { name: 'Dati inseriti' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: 'Dati da non perdere' } })
    fireEvent.click(screen.getByRole('tab', { name: 'Dati estratti' }))
    fireEvent.click(screen.getByRole('button', { name: 'Riestrai dalle fonti' }))
    expect(api.extractCallFacts).not.toHaveBeenCalled()
    confirm.mockReturnValue(true)
    fireEvent.click(screen.getByRole('button', { name: 'Riestrai dalle fonti' }))
    await waitFor(() => expect(api.callFactsReview).toHaveBeenCalledTimes(2))
    await waitFor(() => expect(screen.getByRole('tab', { name: /Dati inseriti/ })).toBeEnabled())
    fireEvent.click(screen.getByRole('tab', { name: /Dati inseriti/ }))
    expect(screen.getByRole('textbox')).toHaveValue('Dati da non perdere')
    expect(api.updateProjectArtifact).not.toHaveBeenCalled()
  })

  it('excludes and restores facts without deleting them', async () => {
    const excluded = structuredClone(review)
    excluded.facts[0].status = 'discarded'
    excluded.discarded_count = 1
    excluded.pending_count = 0
    vi.mocked(api.reviseCallFact).mockResolvedValueOnce(excluded).mockResolvedValueOnce(review)
    setup()
    fireEvent.click(await screen.findByRole('button', { name: 'Escludi' }))
    expect(await screen.findByText('Nessun dato estratto.')).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Esclusi 1' }))
    expect(screen.getByRole('heading', { name: 'Scadenza' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Ripristina' }))
    await screen.findByText('Nessun dato escluso.')
    fireEvent.click(screen.getByRole('button', { name: 'Attivi 1' }))
    expect(screen.getByRole('heading', { name: 'Scadenza' })).toBeVisible()
    expect(api.reviseCallFact).toHaveBeenLastCalledWith('demo', 'cf-scadenza', { action: 'restore', version: 4 })
  })

  it('allows entered data and retry when extracted data fail to load', async () => {
    vi.mocked(api.callFactsReview).mockRejectedValueOnce(new Error('Dati non disponibili'))
    setup()
    expect(await screen.findByRole('alert')).toHaveTextContent('Dati non disponibili')
    fireEvent.click(screen.getByRole('tab', { name: 'Dati inseriti' }))
    expect(screen.getByRole('textbox')).toHaveValue(entered.content)
    fireEvent.click(within(screen.getByRole('alert')).getByRole('button', { name: 'Riprova' }))
    fireEvent.click(screen.getByRole('tab', { name: 'Dati estratti' }))
    expect(await screen.findByRole('heading', { name: 'Scadenza' })).toBeVisible()
  })
})
