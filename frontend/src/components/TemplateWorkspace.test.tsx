import { act, cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { DraftGenerationResult, KnowledgeArtifactDetail } from '../types'
import { TemplateWorkspace } from './TemplateWorkspace'

vi.mock('../api', () => ({ api: {
  projectArtifact: vi.fn(), updateProjectArtifact: vi.fn(), generateDraft: vi.fn(),
} }))

const template: KnowledgeArtifactDetail = {
  id: 'test--template', kind: 'template', title: 'Template', filename: 'template.md',
  scope: 'project', status: 'Bozza', version: 2, updated_at: '', editable: true,
  chunk_count: 1, byte_size: 80,
  content: '---\nartifact: template\n---\n\n# Modello candidatura\n\n## Intervento\n\n[TODO: descrizione]',
}
const blankOutput: KnowledgeArtifactDetail = {
  ...template, id: 'test--draft', kind: 'output_draft', title: 'Draft', filename: 'draft.md',
  status: 'Da generare', version: 1, chunk_count: 0, content: '# Draft\n\nGenerare dal template.',
}
const savedOutput: KnowledgeArtifactDetail = {
  ...blankOutput, status: 'Da verificare', version: 3,
  content: '---\nartifact: output_draft\nstatus: pending_review\n---\n\n# Candidatura compilata\n\nTesto salvato [CF:cf-01].\n\n## Informazioni mancanti\n\n- Importo richiesto',
}
const generation: DraftGenerationResult = {
  artifact: savedOutput, available_fact_count: 2, verified_fact_count: 0, used_fact_count: 1,
  missing_information: ['Importo richiesto'], model: 'test', total_tokens: 1,
}

function setup(initialView: 'model' | 'compilation' = 'model', model = template) {
  const onUpdated = vi.fn()
  const onDirtyChange = vi.fn()
  return { ...render(<TemplateWorkspace projectId="test" template={model}
    outputId={blankOutput.id} initialView={initialView} initialFormat="text" onUpdated={onUpdated} onDirtyChange={onDirtyChange} />),
  onUpdated, onDirtyChange }
}

describe('TemplateWorkspace', () => {
  afterEach(() => { cleanup(); vi.restoreAllMocks() })
  beforeEach(() => {
    vi.mocked(api.projectArtifact).mockReset().mockResolvedValue(blankOutput)
    vi.mocked(api.generateDraft).mockReset().mockResolvedValue(generation)
    vi.mocked(api.updateProjectArtifact).mockReset().mockImplementation(async (_project, id, content) => ({
      ...(id === template.id ? template : savedOutput), content, version: 4, status: 'Bozza aggiornata',
    }))
    vi.spyOn(window, 'confirm').mockReturnValue(true)
  })

  const emptyTemplate = { ...template, content: '', byte_size: 0, version: 1, status: 'Da configurare' }

  it('starts without a fictitious template and disables generation', async () => {
    setup('model', emptyTemplate)
    expect(screen.getByText('Nessun modello caricato')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Carica modello' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Crea modello' })).toBeEnabled()
    expect(screen.queryByRole('textbox')).toBeNull()
    expect(screen.queryByRole('article')).toBeNull()
    await waitFor(() => expect(api.projectArtifact).toHaveBeenCalled())
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Genera compilazione' }))
    expect(api.generateDraft).not.toHaveBeenCalled()
  })

  it('creates a blank model explicitly and requires content and saving before generation', async () => {
    setup('model', emptyTemplate)
    fireEvent.click(screen.getByRole('button', { name: 'Crea modello' }))
    expect(screen.getByRole('textbox', { name: 'Contenuto del modello' })).toHaveValue('')
    expect(screen.getByRole('button', { name: 'Salva modello' })).toBeDisabled()
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Domanda specifica\n\nPEC: [TODO]' } })
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await screen.findByText('Modello salvato.')
    expect(api.updateProjectArtifact).toHaveBeenCalledWith('test', template.id, '# Domanda specifica\n\nPEC: [TODO]')
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled()
    fireEvent.click(screen.getByRole('button', { name: 'Anteprima' }))
    expect(screen.getByRole('heading', { name: 'Domanda specifica' })).toBeVisible()
  })

  it('can leave an empty new model without saving a placeholder', async () => {
    setup('model', emptyTemplate)
    fireEvent.click(screen.getByRole('button', { name: 'Crea modello' }))
    fireEvent.click(screen.getByRole('button', { name: 'Annulla modifiche' }))
    expect(screen.getByText('Nessun modello caricato')).toBeVisible()
    expect(api.updateProjectArtifact).not.toHaveBeenCalled()
    expect(window.confirm).not.toHaveBeenCalled()
  })

  it('imports into an empty model without inserting predefined sections', async () => {
    setup('model', emptyTemplate)
    const content = 'Richiedente: [TODO]\nPEC: [TODO]'
    const file = new File([content], 'modulo.txt')
    Object.defineProperty(file, 'arrayBuffer', { value: async () => new TextEncoder().encode(content).buffer })
    fireEvent.change(screen.getByLabelText('Importa modello Markdown o TXT'), { target: { files: [file] } })
    expect(await screen.findByRole('textbox')).toHaveValue(content)
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled())
    expect(api.updateProjectArtifact).toHaveBeenCalledWith('test', template.id, content)
  })

  it('still displays and edits a saved compilation when the model is absent', async () => {
    vi.mocked(api.projectArtifact).mockResolvedValue(savedOutput)
    setup('compilation', emptyTemplate)
    expect(await screen.findByRole('heading', { name: 'Candidatura compilata' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Modifica testo' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Scarica Markdown' })).toBeEnabled()
    expect(screen.getByRole('button', { name: 'Rigenera compilazione' })).toBeDisabled()
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    expect(screen.getByText('Nessun modello caricato')).toBeVisible()
  })

  it('renders the model as Markdown without exposing YAML or an empty Draft editor', async () => {
    setup()
    expect(screen.getByRole('heading', { name: 'Modello candidatura' })).toBeVisible()
    expect(screen.queryByText('artifact: template')).not.toBeInTheDocument()
    expect(screen.queryByRole('textbox')).not.toBeInTheDocument()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled())
    fireEvent.click(screen.getByRole('tab', { name: 'Compilazione' }))
    expect(screen.getByText('Nessuna compilazione generata')).toBeVisible()
    expect(screen.queryByRole('button', { name: 'Modifica testo' })).not.toBeInTheDocument()
  })

  it('restores existing output and its missing information without regenerating', async () => {
    vi.mocked(api.projectArtifact).mockResolvedValue(savedOutput)
    setup('compilation')
    expect(await screen.findByRole('heading', { name: 'Candidatura compilata' })).toBeVisible()
    expect(screen.getByText('Importo richiesto')).toBeVisible()
    expect(api.generateDraft).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    expect(screen.getByRole('heading', { name: 'Modello candidatura' })).toBeVisible()
  })

  it('generates into the same Template workspace while retaining the model', async () => {
    const { onUpdated } = setup()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled())
    fireEvent.click(screen.getByRole('button', { name: 'Genera compilazione' }))
    expect(await screen.findByRole('heading', { name: 'Candidatura compilata' })).toBeVisible()
    expect(screen.getByRole('heading', { name: 'Moduli e bozze' })).toBeVisible()
    expect(screen.getByRole('tab', { name: 'Compilazione' })).toHaveAttribute('aria-selected', 'true')
    expect(onUpdated).toHaveBeenCalledWith(savedOutput)
    expect(api.generateDraft).toHaveBeenCalledExactlyOnceWith('test')
    expect(api.updateProjectArtifact).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('tab', { name: 'Modello' }))
    expect(screen.getByRole('heading', { name: 'Modello candidatura' })).toBeVisible()
  })

  it('saves model and output to their original separate artifact IDs', async () => {
    vi.mocked(api.projectArtifact).mockResolvedValue(savedOutput)
    setup()
    await screen.findByRole('button', { name: 'Rigenera compilazione' })
    fireEvent.click(screen.getByRole('button', { name: 'Modifica testo' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Modello modificato' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await screen.findByText("Modello salvato. La compilazione precedente non e' stata rigenerata.")
    expect(api.updateProjectArtifact).toHaveBeenLastCalledWith('test', template.id, '# Modello modificato')
    fireEvent.click(screen.getByRole('tab', { name: 'Compilazione' }))
    expect(screen.getByRole('heading', { name: 'Candidatura compilata' })).toBeVisible()
    fireEvent.click(screen.getByRole('button', { name: 'Modifica testo' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Compilazione corretta' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva compilazione' }))
    await screen.findByText('Compilazione salvata.')
    expect(api.updateProjectArtifact).toHaveBeenLastCalledWith('test', savedOutput.id, '# Compilazione corretta')
  })

  it('keeps unsaved text between tabs and blocks generation until both documents are saved', async () => {
    vi.mocked(api.projectArtifact).mockResolvedValue(savedOutput)
    const { onDirtyChange } = setup()
    await screen.findByRole('button', { name: 'Rigenera compilazione' })
    fireEvent.click(screen.getByRole('button', { name: 'Modifica testo' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Modello non salvato' } })
    fireEvent.click(screen.getByRole('tab', { name: 'Compilazione' }))
    expect(screen.getByRole('button', { name: 'Rigenera compilazione' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Modifica testo' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Compilazione non salvata' } })
    fireEvent.click(screen.getByRole('tab', { name: /Modello/ }))
    expect(screen.getByRole('heading', { name: 'Modello non salvato' })).toBeVisible()
    expect(onDirtyChange).toHaveBeenLastCalledWith(true)
    fireEvent.click(screen.getByRole('button', { name: 'Annulla modifiche' }))
    expect(screen.getByRole('button', { name: 'Rigenera compilazione' })).toBeDisabled()
  })

  it('does not overwrite a saved compilation when regeneration is cancelled', async () => {
    vi.mocked(api.projectArtifact).mockResolvedValue(savedOutput)
    vi.mocked(window.confirm).mockReturnValue(false)
    setup('compilation')
    fireEvent.click(await screen.findByRole('button', { name: 'Rigenera compilazione' }))
    expect(window.confirm).toHaveBeenCalled()
    expect(api.generateDraft).not.toHaveBeenCalled()
    expect(screen.getByRole('heading', { name: 'Candidatura compilata' })).toBeVisible()
  })

  it('preserves content and shows a recoverable generation failure', async () => {
    vi.mocked(api.generateDraft).mockRejectedValue(new Error('Servizio di generazione non disponibile'))
    setup()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled())
    fireEvent.click(screen.getByRole('button', { name: 'Genera compilazione' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Servizio di generazione non disponibile')
    expect(screen.getByRole('heading', { name: 'Modello candidatura' })).toBeVisible()
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled()
  })

  it('retains unsaved changes when saving fails', async () => {
    vi.mocked(api.updateProjectArtifact).mockRejectedValue(new Error('Salvataggio non disponibile'))
    setup()
    fireEvent.click(screen.getByRole('button', { name: 'Modifica testo' }))
    fireEvent.change(screen.getByRole('textbox'), { target: { value: '# Non perdere questo testo' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Salvataggio non disponibile')
    expect(screen.getByRole('textbox')).toHaveValue('# Non perdere questo testo')
    expect(screen.getByRole('button', { name: 'Salva modello' })).toBeEnabled()
  })

  it('blocks generation after a load error and supports retrying the saved output', async () => {
    vi.mocked(api.projectArtifact).mockRejectedValueOnce(new Error('Archivio non disponibile'))
    setup('compilation')
    expect(await screen.findByRole('alert')).toHaveTextContent('Archivio non disponibile')
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Riprova' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled())
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  it.each([
    ['modello.pdf', 'pdf', 'Formato non supportato'],
    ['modello.txt', ' ', 'non contiene un modello testuale valido'],
    ['modello.md', 'x'.repeat(50_001), '50.000 caratteri'],
    ['modello.txt', '\0binary', 'non contiene un modello testuale valido'],
  ])('rejects an invalid import: %s', async (name, content, error) => {
    setup()
    const file = new File([content], name)
    Object.defineProperty(file, 'arrayBuffer', { value: async () => new TextEncoder().encode(content).buffer })
    fireEvent.change(screen.getByLabelText('Importa modello Markdown o TXT'), { target: { files: [file] } })
    expect(await screen.findByRole('alert')).toHaveTextContent(error)
    expect(api.updateProjectArtifact).not.toHaveBeenCalled()
    expect(screen.getByRole('heading', { name: 'Modello candidatura' })).toBeVisible()
  })

  it('imports a text file for review without saving automatically', async () => {
    setup()
    const file = new File(['# Nuovo modello'], 'modello.txt')
    Object.defineProperty(file, 'arrayBuffer', { value: async () => new TextEncoder().encode('# Nuovo modello').buffer })
    fireEvent.change(screen.getByLabelText('Importa modello Markdown o TXT'), { target: { files: [file] } })
    expect(await screen.findByRole('textbox')).toHaveValue('# Nuovo modello')
    expect(api.updateProjectArtifact).not.toHaveBeenCalled()
    expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeDisabled()
  })

  it('ignores generation finishing after leaving the workspace', async () => {
    let resolve!: (value: DraftGenerationResult) => void
    vi.mocked(api.generateDraft).mockReturnValue(new Promise((done) => { resolve = done }))
    const { unmount, onUpdated } = setup()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Genera compilazione' })).toBeEnabled())
    fireEvent.click(screen.getByRole('button', { name: 'Genera compilazione' }))
    expect(screen.getByRole('button', { name: 'Generazione in corso' })).toBeDisabled()
    unmount()
    await act(async () => resolve(generation))
    expect(onUpdated).not.toHaveBeenCalled()
  })

  it('does not execute HTML, unsafe links or remote images from model output', async () => {
    vi.mocked(api.projectArtifact).mockResolvedValue({ ...savedOutput,
      content: '# Documento\n\n<script>alert(1)</script>\n\n[link](javascript:alert%281%29)\n\n![immagine](https://example.com/track.png)',
    })
    const { container } = setup('compilation')
    await screen.findByRole('heading', { name: 'Documento' })
    expect(container.querySelector('script')).toBeNull()
    expect(container.querySelector('img')).toBeNull()
    expect(container.querySelector('a')?.getAttribute('href')).not.toContain('javascript:')
  })
})
