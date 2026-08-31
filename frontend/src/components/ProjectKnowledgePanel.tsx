import {
  FileText,
  LoaderCircle,
  NotebookPen,
  Paperclip,
  Pencil,
  Plus,
  X,
} from 'lucide-react'
import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { api } from '../api'
import { useDismissibleMenu } from '../hooks/useDismissibleMenu'
import type { ProjectDetail, ProjectFile } from '../types'
import { ProjectPreparationPanel } from './ProjectPreparationPanel'
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
  const addMenuRef = useDismissibleMenu<HTMLDivElement>(
    addMenuOpen,
    () => setAddMenuOpen(false),
  )

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
            <div className="context-add-wrap" ref={addMenuRef}>
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

        <ProjectPreparationPanel project={project} />
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
