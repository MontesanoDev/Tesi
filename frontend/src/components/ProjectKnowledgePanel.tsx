import {
  ChevronRight,
  ClipboardList,
  FileOutput,
  FileText,
  LayoutTemplate,
  ListChecks,
  LoaderCircle,
  NotebookPen,
  Paperclip,
  Pencil,
  Plus,
  X,
} from 'lucide-react'
import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type {
  KnowledgeArtifactSummary,
  ProjectDetail,
  ProjectFile,
  StatusTone,
} from '../types'
import { StatusPill } from './StatusPill'

interface ProjectKnowledgePanelProps {
  project: ProjectDetail
  onProjectChange: () => Promise<void>
}

function markdownFilename(title: string) {
  const slug = title
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
  return `${slug || 'contenuto'}.md`
}

function fragmentCountLabel(count: number) {
  return count === 1 ? '1 frammento' : `${count} frammenti`
}

function isEditableSource(file: ProjectFile) {
  return file.mime_type === 'text/plain' || file.mime_type === 'text/markdown'
}

function knowledgeItemLabel(name: string, count: number) {
  if (name === 'Company KB' || name === 'General KB') {
    return count === 1 ? '1 documento' : `${count} documenti`
  }
  if (name === 'Modelli') {
    return count === 1 ? '1 disponibile' : `${count} disponibili`
  }
  return count === 1 ? '1 verificato' : `${count} verificati`
}

const WORKFLOW_ITEMS = [
  { kind: 'call_facts', label: 'Call Facts' },
  { kind: 'project_facts', label: 'Dati del progetto' },
  { kind: 'template', label: 'Template' },
  { kind: 'output_draft', label: 'Draft' },
] as const

function workflowTone(status: string): StatusTone {
  if (status === 'Verificato') return 'success'
  if (status === 'Da estrarre' || status === 'Da generare') return 'info'
  if (status === 'Bozza' || status === 'Bozza aggiornata' || status === 'Da verificare') {
    return 'warning'
  }
  return 'purple'
}

function WorkflowIcon({ kind }: { kind: (typeof WORKFLOW_ITEMS)[number]['kind'] }) {
  if (kind === 'call_facts') return <ListChecks size={17} />
  if (kind === 'project_facts') return <ClipboardList size={17} />
  if (kind === 'template') return <LayoutTemplate size={17} />
  return <FileOutput size={17} />
}

export function ProjectKnowledgePanel({
  project,
  onProjectChange,
}: ProjectKnowledgePanelProps) {
  const fileInput = useRef<HTMLInputElement>(null)
  const [addMenuOpen, setAddMenuOpen] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [textModalOpen, setTextModalOpen] = useState(false)
  const [editingFile, setEditingFile] = useState<ProjectFile | null>(null)
  const [loadingEditorId, setLoadingEditorId] = useState<number | null>(null)
  const [textTitle, setTextTitle] = useState('')
  const [textContent, setTextContent] = useState('')
  const [savingText, setSavingText] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [workflowArtifacts, setWorkflowArtifacts] = useState<KnowledgeArtifactSummary[]>([])

  useEffect(() => {
    const controller = new AbortController()
    setWorkflowArtifacts([])
    api.projectArtifacts(project.id, controller.signal)
      .then(setWorkflowArtifacts)
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setWorkflowArtifacts([])
      })
    return () => controller.abort()
  }, [project.id])

  async function uploadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    setAddMenuOpen(false)
    if (!file || uploading) return

    setUploading(true)
    setFeedback(null)
    setError(null)
    try {
      const uploaded = await api.uploadProjectFile(project.id, file)
      await onProjectChange()
      setFeedback(`${uploaded.name} indicizzato in ${fragmentCountLabel(uploaded.chunk_count)}.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Caricamento non riuscito')
    } finally {
      setUploading(false)
    }
  }

  function openTextContentModal() {
    setAddMenuOpen(false)
    setEditingFile(null)
    setTextTitle('')
    setTextContent('')
    setFeedback(null)
    setError(null)
    setTextModalOpen(true)
  }

  async function openFileEditor(file: ProjectFile) {
    if (!isEditableSource(file) || loadingEditorId !== null || savingText) return
    setLoadingEditorId(file.id)
    setFeedback(null)
    setError(null)
    try {
      const detail = await api.projectFileContent(project.id, file.id)
      setEditingFile(file)
      setTextTitle('')
      setTextContent(detail.content)
      setTextModalOpen(true)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Contenuto non disponibile')
    } finally {
      setLoadingEditorId(null)
    }
  }

  function closeTextModal() {
    if (savingText) return
    setTextModalOpen(false)
    setEditingFile(null)
    setTextTitle('')
    setTextContent('')
    setError(null)
  }

  async function saveTextContent(event: FormEvent) {
    event.preventDefault()
    const title = textTitle.trim()
    const content = textContent.trim()
    if (savingText) return
    if (!editingFile && title.length < 3) {
      setError('Inserisci un titolo di almeno 3 caratteri')
      return
    }
    if (content.length < 3) {
      setError('Inserisci un contenuto di almeno 3 caratteri')
      return
    }

    setSavingText(true)
    setFeedback(null)
    setError(null)
    try {
      const file = editingFile
        ? await api.updateProjectFileContent(project.id, editingFile.id, textContent)
        : await api.uploadProjectFile(
            project.id,
            new File(
              [`# ${title}\n\n${content}\n`],
              markdownFilename(title),
              { type: 'text/markdown' },
            ),
          )
      await onProjectChange()
      setTextModalOpen(false)
      setEditingFile(null)
      setTextTitle('')
      setTextContent('')
      setFeedback(
        editingFile
          ? `${file.name} aggiornato e reindicizzato in ${fragmentCountLabel(file.chunk_count)}.`
          : `${file.name} indicizzato in ${fragmentCountLabel(file.chunk_count)}.`,
      )
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      setSavingText(false)
    }
  }

  const sourceCountLabel = project.files.length === 1
    ? '1 fonte'
    : `${project.files.length} fonti`

  function workflowStatus(kind: (typeof WORKFLOW_ITEMS)[number]['kind']) {
    const artifact = workflowArtifacts.find((item) => item.kind === kind)
    if (artifact) return artifact.status
    if (kind === 'call_facts') {
      if (project.call_fact_count === 0) return 'Da estrarre'
      return project.missing_fact_count > 0 ? 'Da verificare' : 'Verificato'
    }
    if (kind === 'output_draft') return 'Da generare'
    return 'Bozza'
  }

  function workflowDetail(kind: (typeof WORKFLOW_ITEMS)[number]['kind']) {
    if (kind === 'call_facts') {
      const factLabel = project.call_fact_count === 1
        ? '1 fatto'
        : `${project.call_fact_count} fatti`
      return `${factLabel} · ${project.missing_fact_count} mancanti`
    }
    const artifact = workflowArtifacts.find((item) => item.kind === kind)
    return artifact ? `Versione ${artifact.version}` : 'Versione 1'
  }

  return (
    <>
      <aside className="knowledge-panel project-context-panel">
        <input
          ref={fileInput}
          className="source-file-input"
          type="file"
          aria-label="Seleziona un documento da indicizzare"
          accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
          onChange={uploadFile}
        />
        <section className="knowledge-section knowledge-files">
          <div className="panel-title-row">
            <div>
              <h2>Contesto progetto</h2>
              <span className="context-source-count">{sourceCountLabel}</span>
            </div>
            <div className="context-add-wrap">
              <button
                className={`icon-button${addMenuOpen ? ' is-active' : ''}`}
                type="button"
                aria-label="Aggiungi al contesto"
                aria-expanded={addMenuOpen}
                disabled={uploading || savingText}
                onClick={() => setAddMenuOpen((value) => !value)}
              >
                {uploading ? <LoaderCircle className="spin" size={18} /> : <Plus size={18} />}
              </button>
              {addMenuOpen && (
                <div className="context-add-menu">
                  <button type="button" onClick={() => fileInput.current?.click()}>
                    <Paperclip size={17} /> Carica dal dispositivo
                  </button>
                  <button type="button" onClick={openTextContentModal}>
                    <NotebookPen size={17} /> Aggiungi contenuto testuale
                  </button>
                </div>
              )}
            </div>
          </div>
          {feedback && (
            <p className="upload-feedback upload-feedback--success" aria-live="polite">
              {feedback}
            </p>
          )}
          {error && !textModalOpen && (
            <p className="upload-feedback upload-feedback--error" role="alert">{error}</p>
          )}
          <div className="file-list context-file-list">
            {project.files.length === 0 ? (
              <p className="empty-list">Nessuna fonte nel progetto</p>
            ) : (
              project.files.map((file) => (
                <div className="file-row context-file-row" key={file.id}>
                  <FileText size={17} />
                  <div>
                    <strong>{file.name}</strong>
                    <span>{file.metadata}</span>
                  </div>
                  <StatusPill tone={file.kind === 'template' ? 'purple' : 'success'}>
                    {file.status}
                  </StatusPill>
                  {isEditableSource(file) ? (
                    <button
                      className="icon-button context-file-edit"
                      type="button"
                      title={`Modifica ${file.name}`}
                      aria-label={`Modifica ${file.name}`}
                      disabled={loadingEditorId !== null || uploading || savingText}
                      onClick={() => openFileEditor(file)}
                    >
                      {loadingEditorId === file.id
                        ? <LoaderCircle className="spin" size={16} />
                        : <Pencil size={16} />}
                    </button>
                  ) : (
                    <span className="context-file-action-spacer" aria-hidden="true" />
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        <section className="knowledge-section knowledge-summary">
          <h2>Conoscenza utilizzata</h2>
          <div className="knowledge-source-list">
            {project.knowledge_sources.length === 0 ? (
              <p className="empty-list">Nessuna conoscenza condivisa disponibile</p>
            ) : (
              project.knowledge_sources.map((source) => (
                <div className="knowledge-source" key={source.id}>
                  <span className={`source-dot source-dot--${source.tone}`} />
                  <strong>{source.name}</strong>
                  <span>{knowledgeItemLabel(source.name, source.item_count)}</span>
                </div>
              ))
            )}
          </div>
        </section>

        <section className="knowledge-section project-workflow-summary">
          <h2>Preparazione candidatura</h2>
          <div className="project-workflow-list">
            {WORKFLOW_ITEMS.map((item) => {
              const status = workflowStatus(item.kind)
              return (
                <Link
                  className="project-workflow-row"
                  key={item.kind}
                  to={`/projects/${project.id}/knowledge?artifact=${item.kind}`}
                >
                  <WorkflowIcon kind={item.kind} />
                  <span>
                    <strong>{item.label}</strong>
                    <small>{workflowDetail(item.kind)}</small>
                  </span>
                  <StatusPill tone={workflowTone(status)}>{status}</StatusPill>
                  <ChevronRight size={16} />
                </Link>
              )
            })}
          </div>
        </section>
      </aside>

      {textModalOpen && (
        <div className="modal-layer" role="presentation">
          <button
            className="modal-scrim"
            type="button"
            aria-label="Chiudi contenuto testuale"
            disabled={savingText}
            onClick={closeTextModal}
          />
          <form
            className="project-modal text-content-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="text-content-modal-title"
            noValidate
            onSubmit={saveTextContent}
          >
            <div className="modal-heading">
              <h2 id="text-content-modal-title">
                {editingFile ? `Modifica ${editingFile.name}` : 'Aggiungi contenuto testuale'}
              </h2>
              <button
                className="icon-button"
                type="button"
                aria-label="Chiudi"
                disabled={savingText}
                onClick={closeTextModal}
              >
                <X size={18} />
              </button>
            </div>
            {!editingFile && (
              <label>
                Titolo
                <input
                  required
                  minLength={3}
                  autoFocus
                  value={textTitle}
                  onChange={(event) => {
                    setTextTitle(event.target.value)
                    setError(null)
                  }}
                />
              </label>
            )}
            <label>
              {editingFile?.mime_type === 'text/plain' ? 'Contenuto testuale' : 'Contenuto Markdown'}
              <textarea
                required
                minLength={3}
                rows={12}
                autoFocus={Boolean(editingFile)}
                spellCheck={false}
                value={textContent}
                onChange={(event) => {
                  setTextContent(event.target.value)
                  setError(null)
                }}
              />
            </label>
            {error && <p className="upload-feedback upload-feedback--error" role="alert">{error}</p>}
            <div className="modal-actions">
              <button className="button" type="button" disabled={savingText} onClick={closeTextModal}>
                Annulla
              </button>
              <button
                className="button button--primary"
                type="submit"
                disabled={
                  savingText
                  || (!editingFile && !textTitle.trim())
                  || !textContent.trim()
                }
              >
                {savingText && <LoaderCircle className="spin" size={15} />}
                {editingFile ? 'Salva modifiche' : 'Aggiungi al progetto'}
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
