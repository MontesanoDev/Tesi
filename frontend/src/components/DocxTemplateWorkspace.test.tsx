import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import { documentCompilationFixture } from '../test/documentCompilationFixture'
import type { DocumentCompilation } from '../types'
import { DocxTemplateWorkspace } from './DocxTemplateWorkspace'

vi.mock('../api', () => ({ api: {
  documentCompilations: vi.fn(), documentCompilation: vi.fn(), compileDocument: vi.fn(), downloadCompilation: vi.fn(),
} }))

const run = documentCompilationFixture()
const docx = () => new File(['test-docx'], 'domanda.docx', { type: 'application/octet-stream' })
const upload = (file = docx()) => fireEvent.change(screen.getByLabelText('Carica modello DOCX'), { target: { files: [file] } })
const openHistory = () => fireEvent.click(screen.getByRole('tab', { name: /Compilazioni salvate/ }))

async function setup() {
  const onDirtyChange = vi.fn()
  const rendered = render(<DocxTemplateWorkspace projectId="docx-test" onDirtyChange={onDirtyChange} />)
  await waitFor(() => expect(api.documentCompilations).toHaveBeenCalled())
  await waitFor(() => expect(screen.queryByText('Caricamento compilazioni Word')).not.toBeInTheDocument())
  return { ...rendered, onDirtyChange }
}

describe('Word Template workspace', () => {
  beforeEach(() => {
    vi.mocked(api.documentCompilations).mockReset().mockResolvedValue([])
    vi.mocked(api.documentCompilation).mockReset().mockResolvedValue(run)
    vi.mocked(api.compileDocument).mockReset().mockResolvedValue(run)
    vi.mocked(api.downloadCompilation).mockReset().mockResolvedValue(new Blob(['docx']))
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })
  afterEach(() => { cleanup(); vi.restoreAllMocks(); vi.unstubAllGlobals() })

  it('uploads only on explicit generation, keeps prior runs and presents grounded results', async () => {
    const { onDirtyChange } = await setup()
    expect(screen.getByRole('button', { name: 'Compila Word' })).toBeDisabled()
    const file = docx()
    upload(file)
    fireEvent.change(screen.getByLabelText(/Indicazioni per la compilazione/), { target: { value: '  Partecipazione singola  ' } })
    expect(api.compileDocument).not.toHaveBeenCalled()
    expect(onDirtyChange).toHaveBeenLastCalledWith(true)
    fireEvent.click(screen.getByRole('button', { name: 'Compila Word' }))
    expect(await screen.findByRole('button', { name: 'Scarica Word compilato' })).toBeEnabled()
    expect(api.compileDocument).toHaveBeenCalledExactlyOnceWith('docx-test', file, 'Partecipazione singola')
    expect(screen.getByText('Mapi Ingegneria S.r.l.')).toBeVisible()
    expect(screen.getByText('Bozza non verificata. Nessuna firma o invio eseguiti.')).toBeVisible()
    expect(onDirtyChange).toHaveBeenLastCalledWith(false)
    expect(api.documentCompilation).not.toHaveBeenCalled()
    fireEvent.click(screen.getByText('Ragione sociale'))
    expect(screen.getByText('Denominazione: Mapi Ingegneria S.r.l.')).toBeVisible()
    expect(screen.getByText('visura-simulata.pdf · Frammento 2')).toBeVisible()
    expect(screen.queryByText(/Pagina/)).not.toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Filtra campi'), { target: { value: 'unresolved' } })
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    expect(screen.getByText('Codice fiscale del firmatario')).toBeVisible()
    expect(screen.queryByText('Mandanti del raggruppamento')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Qualifica del firmatario'))
    expect(screen.getByText('Proposta non inserita:')).toBeVisible()
    expect(screen.getByText('Il valore non compare letteralmente nelle evidenze citate')).toBeVisible()
  })

  it.each(['bando.pdf', 'modello.doc', 'modello.txt'])('rejects unsupported %s without losing a valid model', async (name) => {
    await setup()
    upload()
    upload(new File(['wrong'], name))
    expect(screen.getByRole('alert')).toHaveTextContent('Formato non supportato')
    expect(screen.getByText('domanda.docx')).toBeVisible()
    expect(api.compileDocument).not.toHaveBeenCalled()
  })

  it('rejects empty and oversized uploads and constrains instructions', async () => {
    await setup()
    upload(new File([], 'empty.docx'))
    expect(screen.getByRole('alert')).toHaveTextContent('vuoto')
    const large = docx()
    Object.defineProperty(large, 'size', { value: 20 * 1024 * 1024 + 1 })
    upload(large)
    expect(screen.getByRole('alert')).toHaveTextContent('20 MB')
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveAttribute('maxLength', '4000')
  })

  it('blocks duplicate generation and restores the upload after provider failure', async () => {
    let fail!: (error: Error) => void
    vi.mocked(api.compileDocument).mockImplementation(() => new Promise((_resolve, reject) => { fail = reject }))
    const { onDirtyChange } = await setup()
    upload()
    fireEvent.click(screen.getByRole('button', { name: 'Compila Word' }))
    const progress = screen.getByRole('button', { name: 'Compilazione in corso' })
    fireEvent.click(progress)
    expect(progress).toBeDisabled()
    expect(api.compileDocument).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('button', { name: 'Cambia modello' })).toBeDisabled()
    await act(async () => fail(new Error('Risposta del modello non valida')))
    expect(screen.getByRole('alert')).toHaveTextContent('Risposta del modello non valida')
    expect(screen.getByText('domanda.docx')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Compila Word' })).toBeEnabled()
    expect(onDirtyChange).toHaveBeenLastCalledWith(true)
  })

  it('starts clean, opens saved reports only on request and explicitly reuses the original', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([run])
    await setup()
    expect(screen.getByRole('tab', { name: 'Nuova compilazione' })).toHaveAttribute('aria-selected', 'true')
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    expect(api.documentCompilation).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Compila Word' })).toBeDisabled()
    openHistory()
    await screen.findByText('Ragione sociale')
    expect(api.compileDocument).not.toHaveBeenCalled()
    expect(screen.queryByRole('button', { name: 'Compila Word' })).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Riutilizza modello' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Compila Word' })).toBeEnabled())
    expect(api.downloadCompilation).toHaveBeenCalledWith('docx-test', run.id, 'template')
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue(run.report.instructions)
    expect(api.compileDocument).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Compila Word' }))
    await waitFor(() => expect(api.compileDocument).toHaveBeenCalled())
    const uploaded = vi.mocked(api.compileDocument).mock.calls[0][1]
    expect(uploaded.name).toBe(run.template_name)
    expect(uploaded.type).toContain('wordprocessingml')
  })

  it('ignores stale reports when switching history entries', async () => {
    const second = { ...documentCompilationFixture('docx-test', 'run-2'), template_name: 'secondo.docx' }
    let finish!: (result: DocumentCompilation) => void
    vi.mocked(api.documentCompilations).mockResolvedValue([run, second])
    vi.mocked(api.documentCompilation).mockImplementation((_project, id) => id === run.id
      ? new Promise((resolve) => { finish = resolve }) : Promise.resolve(second))
    await setup()
    openHistory()
    fireEvent.change(screen.getByLabelText('Compilazioni salvate'), { target: { value: second.id } })
    expect(await screen.findByRole('heading', { name: 'secondo.docx' })).toBeVisible()
    await act(async () => finish(run))
    expect(screen.queryByRole('heading', { name: run.template_name })).not.toBeInTheDocument()
  })

  it('recovers from list and detail errors', async () => {
    vi.mocked(api.documentCompilations).mockRejectedValueOnce(new Error('Storico non disponibile')).mockResolvedValue([run])
    vi.mocked(api.documentCompilation).mockRejectedValueOnce(new Error('Report non disponibile')).mockResolvedValue(run)
    await setup()
    expect(screen.getByRole('alert')).toHaveTextContent('Storico non disponibile')
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica compilazioni' }))
    await waitFor(() => expect(screen.getByRole('tab', { name: /Compilazioni salvate/ })).toBeEnabled())
    openHistory()
    await screen.findByText('Report non disponibile')
    fireEvent.click(screen.getByRole('button', { name: 'Riprova' }))
    await screen.findByText('Ragione sociale')
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it('shows download failures without leaving the page or losing the report', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([run])
    vi.mocked(api.downloadCompilation).mockRejectedValue(new Error('File non disponibile'))
    await setup()
    openHistory()
    fireEvent.click(await screen.findByRole('button', { name: 'Scarica Word compilato' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('File non disponibile')
    expect(screen.getByText('Ragione sociale')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Scarica Word compilato' })).toBeEnabled()
  })

  it('reports partial coverage and unclassified cells separately from missing fields', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([run])
    await setup()
    openHistory()
    fireEvent.click(await screen.findByText('Avvisi e copertura fonti (2)'))
    expect(screen.getByText('60 / 80 frammenti utilizzati · Contesto parziale')).toBeVisible()
    expect(screen.getByText(/Elementi non classificati, non necessariamente campi mancanti:/)).toBeVisible()
    fireEvent.change(screen.getByLabelText('Filtra campi'), { target: { value: 'written' } })
    const results = screen.getByRole('region', { name: 'Compilazioni Word' })
    expect(within(results).getByText('Inserito')).toBeVisible()
    expect(within(results).queryByText('Verificato')).not.toBeInTheDocument()
  })

  it('warns before leaving with a selected model and ignores a late generation after unmount', async () => {
    let finish!: (result: DocumentCompilation) => void
    vi.mocked(api.compileDocument).mockImplementation(() => new Promise((resolve) => { finish = resolve }))
    const { unmount, onDirtyChange } = await setup()
    upload()
    const event = new Event('beforeunload', { cancelable: true })
    window.dispatchEvent(event)
    expect(event.defaultPrevented).toBe(true)
    fireEvent.click(screen.getByRole('button', { name: 'Compila Word' }))
    unmount()
    await act(async () => finish(run))
    expect(onDirtyChange).toHaveBeenLastCalledWith(false)
    expect(api.documentCompilation).not.toHaveBeenCalled()
  })

  it('shows paragraph locations and unsupported content in v2 reports while retaining legacy reports', async () => {
    const paragraphs = documentCompilationFixture()
    paragraphs.report.schema_version = 2
    paragraphs.report.unclassified_fields = ['p2.s0', ...paragraphs.report.unclassified_cells]
    paragraphs.report.unsupported_locations = [{ paragraph: 9, reason: 'Controllo Word non modificato' }]
    paragraphs.report.fields[0].cell_id = 'p0.s0'
    paragraphs.report.fields[0].location = { kind: 'paragraph', paragraph: 1, slot: 1, placeholder: '{{ragione_sociale}}' }
    vi.mocked(api.documentCompilations).mockResolvedValue([paragraphs])
    vi.mocked(api.documentCompilation).mockResolvedValue(paragraphs)
    await setup()
    openHistory()
    fireEvent.click(await screen.findByText('Ragione sociale'))
    expect(screen.getByText('Paragrafo 1 · Campo 1 · p0.s0')).toBeVisible()
    expect(screen.queryByText('Cella p0.s0')).not.toBeInTheDocument()
    fireEvent.click(screen.getByText('Avvisi e copertura fonti (2)'))
    expect(screen.getByText('Paragrafo 9: Controllo Word non modificato')).toBeVisible()
    expect(screen.getByText(/Elementi non classificati, non necessariamente campi mancanti:/)).toHaveTextContent('p2.s0')
  })

  it('shows v3 user provenance, rejected citations and the repair audit without marking data verified', async () => {
    const report = documentCompilationFixture()
    report.report.schema_version = 3
    const inserted = report.report.fields[0]
    inserted.evidence[0] = {
      ...inserted.evidence[0], source_id: 'user:instructions', origin: 'user', scope: 'user',
      document_id: null, fragment: null, source_kind: 'user_instructions',
      source_name: 'Indicazioni della compilazione',
    }
    inserted.repair = {
      status: 'corrected', attempted: true, message: 'Correzione applicata; bozza da revisionare',
      initial_proposal: { value: 'Mapi', validation_notes: ['Citazione iniziale non valida'], rejected_evidence: [] },
    }
    const blocked = report.report.fields[1]
    blocked.status = 'needs_review'
    blocked.validation_notes = ['La citazione non compare nella fonte indicata']
    blocked.rejected_evidence = [{ source_id: 'project:999', quote: 'Testo non fornito', reason: 'Fonte non fornita' }]
    blocked.repair = {
      status: 'unresolved', attempted: true, message: 'Proposta ancora bloccata; campo lasciato vuoto',
      initial_proposal: { value: null, validation_notes: ['Fonte assente'], rejected_evidence: blocked.rejected_evidence },
    }
    vi.mocked(api.documentCompilations).mockResolvedValue([report])
    vi.mocked(api.documentCompilation).mockResolvedValue(report)
    await setup()
    openHistory()
    fireEvent.click(await screen.findByText('Ragione sociale'))
    expect(screen.getByText("Indicazioni della compilazione · Dato dichiarato dall'utente")).toBeVisible()
    expect(screen.queryByText(/Frammento null/)).not.toBeInTheDocument()
    expect(screen.getByText('Correzione automatica applicata')).toBeVisible()
    expect(screen.getByText('Proposta iniziale: Mapi')).toBeVisible()
    expect(screen.getByText('Controllo iniziale: Citazione iniziale non valida')).toBeVisible()
    fireEvent.click(screen.getByText('Codice fiscale del firmatario'))
    expect(screen.getByText('Riferimenti rifiutati')).toBeVisible()
    expect(screen.getByText('project:999: Testo non fornito (Fonte non fornita)')).toBeVisible()
    expect(screen.getByText('Correzione non applicata')).toBeVisible()
    expect(screen.getAllByText('Bloccato')).toHaveLength(2)
    expect(screen.queryByText('Verificato')).not.toBeInTheDocument()
  })

  it('resets the form and errors without removing saved history or making API calls', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([run])
    vi.mocked(api.compileDocument).mockRejectedValue(new Error('Citazione non valida'))
    const { onDirtyChange } = await setup()
    upload()
    fireEvent.change(screen.getByLabelText(/Indicazioni per la compilazione/), { target: { value: 'Prova' } })
    fireEvent.click(screen.getByRole('button', { name: 'Compila Word' }))
    await screen.findByRole('alert')
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    vi.mocked(window.confirm).mockReturnValueOnce(false)
    fireEvent.click(screen.getByRole('button', { name: 'Reimposta compilazione' }))
    expect(screen.getByText('domanda.docx')).toBeVisible()
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue('Prova')
    fireEvent.click(screen.getByRole('button', { name: 'Reimposta compilazione' }))
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(screen.queryByText('domanda.docx')).not.toBeInTheDocument()
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue('')
    expect(screen.getByRole('button', { name: 'Compila Word' })).toBeDisabled()
    expect(onDirtyChange).toHaveBeenLastCalledWith(false)
    openHistory()
    await screen.findByText('Ragione sociale')
    expect(api.compileDocument).toHaveBeenCalledTimes(1)
    expect(screen.getByRole('tab', { name: 'Compilazioni salvate (1)' })).toBeVisible()
  })

  it('removing an upload clears its error and never reveals an older result', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([run])
    await setup()
    upload()
    upload(new File(['bad'], 'modello.pdf'))
    expect(screen.getByRole('alert')).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Rimuovi modello selezionato' }))
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Compila Word' })).toBeDisabled()
  })

  it('groups three models by filename and downloads or reuses only the selected run', async () => {
    const second = { ...documentCompilationFixture('docx-test', 'run-2'), template_name: 'allegato.docx' }
    const third = { ...documentCompilationFixture('docx-test', 'run-3'), template_name: 'dichiarazione.docx' }
    const revision = { ...documentCompilationFixture('docx-test', 'run-4'), template_name: run.template_name }
    const saved = [run, second, third, revision]
    vi.mocked(api.documentCompilations).mockResolvedValue(saved)
    vi.mocked(api.documentCompilation).mockImplementation(async (_project, id) => saved.find((item) => item.id === id)!)
    await setup()
    openHistory()
    await screen.findByText('Ragione sociale')
    const history = screen.getByLabelText('Compilazioni salvate')
    expect(history.querySelectorAll('optgroup')).toHaveLength(3)
    expect(history.querySelector('optgroup')?.querySelectorAll('option')).toHaveLength(2)
    for (const item of [second, third, revision]) {
      fireEvent.change(history, { target: { value: item.id } })
      await screen.findByRole('heading', { name: item.template_name })
      vi.mocked(api.downloadCompilation).mockRejectedValueOnce(new Error('Download di prova'))
      fireEvent.click(screen.getByRole('button', { name: 'Modello originale' }))
      await screen.findByRole('alert')
      expect(api.downloadCompilation).toHaveBeenLastCalledWith('docx-test', item.id, 'template')
    }
    fireEvent.click(screen.getByRole('button', { name: 'Riutilizza modello' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Compila Word' })).toBeEnabled())
    expect(api.downloadCompilation).toHaveBeenLastCalledWith('docx-test', revision.id, 'template')
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(api.compileDocument).not.toHaveBeenCalled()
  })

  it('keeps pending inputs while browsing history and ignores report requests after returning to new', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([run])
    let finish!: (result: DocumentCompilation) => void
    vi.mocked(api.documentCompilation).mockImplementation(() => new Promise((resolve) => { finish = resolve }))
    await setup()
    upload()
    fireEvent.change(screen.getByLabelText(/Indicazioni per la compilazione/), { target: { value: 'Indicazioni da conservare' } })
    openHistory()
    expect(screen.getByText('Caricamento report')).toBeVisible()
    fireEvent.click(screen.getByRole('tab', { name: /Nuova compilazione/ }))
    await act(async () => finish(run))
    expect(screen.getByText('domanda.docx')).toBeVisible()
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue('Indicazioni da conservare')
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Reimposta compilazione' }))
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue('')
    expect(api.compileDocument).not.toHaveBeenCalled()
  })

  it('supports keyboard tab navigation and recovers a history load while the saved tab is open', async () => {
    vi.mocked(api.documentCompilations).mockRejectedValueOnce(new Error('Storico offline')).mockResolvedValue([run])
    await setup()
    const newTab = screen.getByRole('tab', { name: 'Nuova compilazione' })
    fireEvent.keyDown(newTab, { key: 'ArrowRight' })
    expect(screen.getByRole('tab', { name: /Compilazioni salvate/ })).toHaveFocus()
    fireEvent.click(screen.getByRole('button', { name: 'Ricarica compilazioni' }))
    await screen.findByText('Ragione sociale')
    expect(screen.getByLabelText('Compilazioni salvate')).toHaveValue(run.id)
    fireEvent.keyDown(screen.getByRole('tab', { name: /Compilazioni salvate/ }), { key: 'Home' })
    expect(newTab).toHaveFocus()
    expect(screen.queryByText('Ragione sociale')).not.toBeInTheDocument()
    expect(screen.getByLabelText(/Indicazioni per la compilazione/)).toHaveValue('')
  })
})
