import {
  FileText,
  LoaderCircle,
  NotebookPen,
  Paperclip,
  Pencil,
  Plus,
  Trash2,
  X,
} from 'lucide-react'
import { useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { api } from '../api'
import { fragmentCountLabel, markdownFilename } from '../sourceText'
import { useDismissibleMenu } from '../hooks/useDismissibleMenu'
import type { ProjectDetail, ProjectFile } from '../types'
import { StatusPill } from './StatusPill'
import { ProjectFormsPanel } from './ProjectFormsPanel'

interface ProjectKnowledgePanelProps {
  project: ProjectDetail
  onProjectChange: () => Promise<void>
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
  const [fileToDelete, setFileToDelete] = useState<ProjectFile | null>(null)
  const [deletingFile, setDeletingFile] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const deleteTrigger = useRef<HTMLButtonElement | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const addMenuRef = useDismissibleMenu<HTMLDivElement>(
    addMenuOpen,
    () => setAddMenuOpen(false),
  )
  const sourceBusy = uploading || savingText || loadingEditorId !== null || deletingFile

  function closeDeleteDialog() {
    if (deletingFile) return
    setFileToDelete(null)
    setDeleteError(null)
    deleteTrigger.current?.focus()
  }

  async function deleteSource() {
    if (!fileToDelete || sourceBusy) return
    const file = fileToDelete
    setDeletingFile(true)
    setDeleteError(null)
    setFeedback(null)
    setError(null)
    try {
      await api.deleteProjectFile(project.id, file.id)
    } catch (reason) {
      setDeleteError(reason instanceof Error ? reason.message : 'Eliminazione non riuscita')
      setDeletingFile(false)
      return
    }
    setFileToDelete(null)
    try {
      await onProjectChange()
      setFeedback(`${file.name} eliminato dal progetto e dall'indice.`)
    } catch {
      setError('Fonte eliminata, ma la lista non si aggiorna. Ricarica la pagina.')
    } finally {
      setDeletingFile(false)
    }
  }

  async function uploadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    setAddMenuOpen(false)
    if (!file || sourceBusy) return

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
    if (!isEditableSource(file) || sourceBusy) return
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

  const sources = project.files.filter((file) => file.kind !== 'form')
  const sourceCountLabel = sources.length === 1
    ? '1 fonte'
    : `${sources.length} fonti`

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
                disabled={sourceBusy}
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
            {sources.length === 0 ? (
              <p className="empty-list">Nessuna fonte nel progetto</p>
            ) : (
              sources.map((file) => (
                <div className="file-row context-file-row" key={file.id}>
                  <FileText size={17} />
                  <div>
                    <strong title={file.name}>{file.name}</strong>
                    <span>{file.metadata}</span>
                  </div>
                  <StatusPill tone={file.kind === 'template' ? 'purple' : 'success'}>
                    {file.status}
                  </StatusPill>
                  <div className="context-file-actions">
                    {isEditableSource(file) ? (
                      <button
                        className="icon-button context-file-edit"
                        type="button"
                        title={`Modifica ${file.name}`}
                        aria-label={`Modifica ${file.name}`}
                        disabled={sourceBusy}
                        onClick={() => openFileEditor(file)}
                      >
                        {loadingEditorId === file.id
                          ? <LoaderCircle className="spin" size={16} />
                          : <Pencil size={16} />}
                      </button>
                    ) : (
                      <span className="context-file-action-spacer" aria-hidden="true" />
                    )}
                    {file.kind === 'source' && (
                      <button
                        className="icon-button context-file-delete"
                        type="button"
                        title={`Elimina ${file.name}`}
                        aria-label={`Elimina ${file.name}`}
                        disabled={sourceBusy}
                        onClick={(event) => {
                          deleteTrigger.current = event.currentTarget
                          setAddMenuOpen(false)
                          setDeleteError(null)
                          setFileToDelete(file)
                        }}
                      >
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </section>
        <ProjectFormsPanel key={project.id} projectId={project.id}
          forms={project.files.filter((file) => file.kind === 'form')} onProjectChange={onProjectChange} />
      </aside>

      {fileToDelete && (
        <div className="modal-layer" role="presentation">
          <button className="modal-scrim" type="button" tabIndex={-1}
            aria-label="Chiudi conferma eliminazione fonte" disabled={deletingFile}
            onClick={closeDeleteDialog} />
          <section className="project-modal delete-project-modal delete-source-modal" role="dialog"
            aria-modal="true" aria-labelledby="delete-source-title"
            aria-describedby="delete-source-description" aria-busy={deletingFile}
            onKeyDown={(event) => {
              if (event.key === 'Escape') {
                event.preventDefault()
                closeDeleteDialog()
              }
              if (event.key === 'Tab') {
                const buttons = event.currentTarget.querySelectorAll<HTMLButtonElement>('button:not(:disabled)')
                const first = buttons[0]
                const last = buttons[buttons.length - 1]
                if (!buttons.length) {
                  event.preventDefault()
                } else if (event.shiftKey && document.activeElement === first) {
                  event.preventDefault()
                  last?.focus()
                } else if (!event.shiftKey && document.activeElement === last) {
                  event.preventDefault()
                  first?.focus()
                }
              }
            }}>
            <div className="modal-heading">
              <h2 id="delete-source-title">Elimina fonte</h2>
              <button className="icon-button" type="button" aria-label="Chiudi"
                disabled={deletingFile} onClick={closeDeleteDialog}><X size={18} /></button>
            </div>
            <p id="delete-source-description">
              Eliminare <strong>{fileToDelete.name}</strong> dal progetto e dall'indice di ricerca?
              Questa operazione non può essere annullata.
            </p>
            <p className="delete-project-note">
              Le conversazioni, i dati già estratti e le compilazioni salvate restano invariati.
            </p>
            {deleteError && <p className="upload-feedback upload-feedback--error" role="alert">{deleteError}</p>}
            <div className="modal-actions">
              <button className="button" type="button" autoFocus disabled={deletingFile}
                onClick={closeDeleteDialog}>Annulla</button>
              <button className="button button--danger" type="button" disabled={deletingFile}
                onClick={deleteSource}>
                {deletingFile ? <LoaderCircle className="spin" size={16} /> : <Trash2 size={16} />}
                {deletingFile ? 'Eliminazione' : 'Elimina fonte'}
              </button>
            </div>
          </section>
        </div>
      )}

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
              Contenuto testuale
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
