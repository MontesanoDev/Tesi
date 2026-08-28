import {
  BookOpen,
  Building2,
  Database,
  FileText,
  LoaderCircle,
  NotebookPen,
  Pencil,
  Trash2,
  Upload,
  X,
} from 'lucide-react'
import { useEffect, useRef, useState, type ChangeEvent, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import type { GlobalKnowledgeDocument, GlobalKnowledgeOverview } from '../types'

type KnowledgeView = 'company' | 'general'

const viewCopy = {
  company: {
    title: 'Company KB',
    description: 'Documenti aziendali, referenze, curriculum e certificazioni.',
    empty: 'Nessun documento aziendale caricato.',
  },
  general: {
    title: 'General KB',
    description: 'Norme, linee guida e materiale tecnico riutilizzabile nei progetti.',
    empty: 'Nessun documento tecnico generale caricato.',
  },
} as const

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

export function CompanyKnowledgePage() {
  const [activeView, setActiveView] = useState<KnowledgeView>('company')
  const [knowledge, setKnowledge] = useState<GlobalKnowledgeOverview | null>(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [textModalOpen, setTextModalOpen] = useState(false)
  const [textTitle, setTextTitle] = useState('')
  const [textContent, setTextContent] = useState('')
  const [savingText, setSavingText] = useState(false)
  const [editingDocument, setEditingDocument] = useState<GlobalKnowledgeDocument | null>(null)
  const [loadingEditorId, setLoadingEditorId] = useState<number | null>(null)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const controller = new AbortController()
    api.globalKnowledge(controller.signal)
      .then((overview) => {
        setKnowledge(overview)
        setError(null)
      })
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setError(reason instanceof Error ? reason.message : 'Conoscenza globale non disponibile')
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false)
      })
    return () => controller.abort()
  }, [])

  const documents = knowledge?.documents.filter((document) => document.category === activeView) ?? []
  const documentCount = documents.length
  const documentCountLabel = documentCount === 1 ? '1 documento' : `${documentCount} documenti`

  function selectView(view: KnowledgeView) {
    setActiveView(view)
    setFeedback(null)
    setError(null)
  }

  async function refreshKnowledge() {
    setKnowledge(await api.globalKnowledge())
  }

  async function uploadDocument(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file || uploading) return
    setUploading(true)
    setFeedback(null)
    setError(null)
    try {
      const document = await api.uploadGlobalKnowledgeFile(file, activeView)
      await refreshKnowledge()
      setFeedback(
        `${document.name} aggiunto a ${viewCopy[activeView].title} in ${fragmentCountLabel(document.chunk_count)}.`,
      )
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Caricamento non riuscito')
    } finally {
      setUploading(false)
    }
  }

  function closeTextModal() {
    if (savingText) return
    setTextModalOpen(false)
    setEditingDocument(null)
    setTextTitle('')
    setTextContent('')
    setError(null)
  }

  function openTextContentModal() {
    setEditingDocument(null)
    setTextTitle('')
    setTextContent('')
    setError(null)
    setTextModalOpen(true)
  }

  async function openDocumentEditor(document: GlobalKnowledgeDocument) {
    if (loadingEditorId !== null || savingText) return
    setLoadingEditorId(document.id)
    setFeedback(null)
    setError(null)
    try {
      const detail = await api.globalKnowledgeFileContent(document.id)
      setEditingDocument(document)
      setTextTitle('')
      setTextContent(detail.content)
      setTextModalOpen(true)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Contenuto non disponibile')
    } finally {
      setLoadingEditorId(null)
    }
  }

  async function saveTextContent(event: FormEvent) {
    event.preventDefault()
    const title = textTitle.trim()
    const content = textContent.trim()
    if ((!editingDocument && !title) || !content || savingText) return

    setSavingText(true)
    setFeedback(null)
    setError(null)
    try {
      const document = editingDocument
        ? await api.updateGlobalKnowledgeFileContent(editingDocument.id, textContent)
        : await api.uploadGlobalKnowledgeFile(
            new File(
              [`# ${title}\n\n${content}\n`],
              markdownFilename(title),
              { type: 'text/markdown' },
            ),
            activeView,
          )
      await refreshKnowledge()
      setTextModalOpen(false)
      setEditingDocument(null)
      setTextTitle('')
      setTextContent('')
      setFeedback(
        editingDocument
          ? `${document.name} aggiornato e reindicizzato in ${fragmentCountLabel(document.chunk_count)}.`
          : `${document.name} aggiunto a ${viewCopy[activeView].title} in ${fragmentCountLabel(document.chunk_count)}.`,
      )
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      setSavingText(false)
    }
  }

  async function deleteDocument(documentId: number, name: string) {
    if (deletingId !== null) return
    setDeletingId(documentId)
    setFeedback(null)
    setError(null)
    try {
      await api.deleteGlobalKnowledgeFile(documentId)
      await refreshKnowledge()
      setFeedback(`${name} rimosso dall'archivio globale.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Rimozione non riuscita')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <AppShell active="company">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="settings-page company-knowledge-page page-container">
        <header className="page-heading">
          <h1>Dati aziendali e conoscenza</h1>
          <p>Gestisci le fonti globali disponibili nei progetti</p>
        </header>

        <div className="knowledge-type-tabs" role="tablist" aria-label="Tipo di conoscenza globale">
          <button
            className={activeView === 'company' ? 'is-active' : ''}
            type="button"
            role="tab"
            aria-selected={activeView === 'company'}
            onClick={() => selectView('company')}
          >
            <Building2 size={16} /> Company KB
          </button>
          <button
            className={activeView === 'general' ? 'is-active' : ''}
            type="button"
            role="tab"
            aria-selected={activeView === 'general'}
            onClick={() => selectView('general')}
          >
            <BookOpen size={16} /> General KB
          </button>
        </div>

        <section className="settings-card company-knowledge-card">
          {loading ? (
            <LoadingState label="Caricamento conoscenza globale" />
          ) : (
            <>
              <div className="global-knowledge-heading">
                <div>
                  <h2>{viewCopy[activeView].title}</h2>
                  <p>{viewCopy[activeView].description}</p>
                </div>
                <div className="global-knowledge-actions">
                  <input
                    ref={fileInput}
                    className="source-file-input"
                    type="file"
                    accept=".pdf,.txt,.md,application/pdf,text/plain,text/markdown"
                    onChange={uploadDocument}
                  />
                  <button
                    className="button button--compact global-upload-button"
                    type="button"
                    disabled={uploading || savingText}
                    onClick={() => fileInput.current?.click()}
                  >
                    {uploading ? <LoaderCircle className="spin" size={15} /> : <Upload size={15} />}
                    {uploading ? 'Indicizzazione' : 'Carica dal dispositivo'}
                  </button>
                  <button
                    className="button button--compact global-upload-button"
                    type="button"
                    disabled={uploading || savingText}
                    onClick={openTextContentModal}
                  >
                    <NotebookPen size={15} />
                    Aggiungi contenuto testuale
                  </button>
                </div>
              </div>
              <div className="settings-card-divider" />
              <div className="setting-section-title">
                <span>{documentCountLabel}</span>
                <small>
                  {documents.reduce((total, document) => total + document.chunk_count, 0)} frammenti indicizzati
                </small>
              </div>
              {documents.length ? (
                <div className="company-document-list">
                  {documents.map((document) => (
                    <div className="company-document-row" key={document.id}>
                      <FileText size={17} />
                      <div>
                        <strong>{document.name}</strong>
                        <span>{document.metadata}</span>
                      </div>
                      <StatusPill tone="success">{document.status}</StatusPill>
                      {document.mime_type === 'text/plain' || document.mime_type === 'text/markdown' ? (
                        <button
                          className="icon-button company-document-edit"
                          type="button"
                          title={`Modifica ${document.name}`}
                          aria-label={`Modifica ${document.name}`}
                          disabled={deletingId !== null || loadingEditorId !== null || uploading}
                          onClick={() => openDocumentEditor(document)}
                        >
                          {loadingEditorId === document.id
                            ? <LoaderCircle className="spin" size={16} />
                            : <Pencil size={16} />}
                        </button>
                      ) : (
                        <span className="company-document-action-spacer" aria-hidden="true" />
                      )}
                      <button
                        className="icon-button company-document-delete"
                        type="button"
                        title={`Rimuovi ${document.name}`}
                        aria-label={`Rimuovi ${document.name}`}
                        disabled={deletingId !== null || loadingEditorId !== null || uploading}
                        onClick={() => deleteDocument(document.id, document.name)}
                      >
                        {deletingId === document.id
                          ? <LoaderCircle className="spin" size={16} />
                          : <Trash2 size={16} />}
                      </button>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="company-kb-empty">
                  <Database size={20} />
                  <span>{viewCopy[activeView].empty}</span>
                </div>
              )}
            </>
          )}
          {feedback && <p className="upload-feedback upload-feedback--success" aria-live="polite">{feedback}</p>}
          {error && !textModalOpen && <p className="upload-feedback upload-feedback--error" role="alert">{error}</p>}
        </section>
      </div>

      {textModalOpen && (
        <div className="modal-layer" role="presentation">
          <button
            className="modal-scrim"
            type="button"
            aria-label="Chiudi contenuto testuale"
            disabled={savingText}
            onClick={closeTextModal}
          />
          <form className="project-modal text-content-modal" onSubmit={saveTextContent}>
            <div className="modal-heading">
              <h2>{editingDocument ? `Modifica ${editingDocument.name}` : 'Aggiungi contenuto testuale'}</h2>
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
            {!editingDocument && (
              <label>
                Titolo
                <input
                  required
                  minLength={3}
                  autoFocus
                  value={textTitle}
                  onChange={(event) => setTextTitle(event.target.value)}
                />
              </label>
            )}
            <label>
              {editingDocument?.mime_type === 'text/plain' ? 'Contenuto testuale' : 'Contenuto Markdown'}
              <textarea
                required
                minLength={3}
                rows={12}
                autoFocus={Boolean(editingDocument)}
                spellCheck={false}
                value={textContent}
                onChange={(event) => setTextContent(event.target.value)}
              />
            </label>
            {error && <p className="upload-feedback upload-feedback--error" role="alert">{error}</p>}
            <div className="modal-actions">
              <button
                className="button"
                type="button"
                disabled={savingText}
                onClick={closeTextModal}
              >
                Annulla
              </button>
              <button
                className="button button--primary"
                type="submit"
                disabled={(!editingDocument && !textTitle.trim()) || !textContent.trim() || savingText}
              >
                {savingText && <LoaderCircle className="spin" size={15} />}
                {editingDocument ? 'Salva modifiche' : `Salva in ${viewCopy[activeView].title}`}
              </button>
            </div>
          </form>
        </div>
      )}
    </AppShell>
  )
}
