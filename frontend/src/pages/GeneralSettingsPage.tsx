import { Database, FileText, LoaderCircle, Trash2, Upload } from 'lucide-react'
import { useEffect, useRef, useState, type ChangeEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import type { GlobalKnowledgeOverview } from '../types'

export function GeneralSettingsPage() {
  const [reviewRequired, setReviewRequired] = useState(true)
  const [knowledge, setKnowledge] = useState<GlobalKnowledgeOverview | null>(null)
  const [knowledgeLoading, setKnowledgeLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)
  const documentCount = knowledge?.document_count ?? 0
  const documentCountLabel = documentCount === 1 ? '1 documento' : `${documentCount} documenti`

  useEffect(() => {
    const controller = new AbortController()
    api.globalKnowledge(controller.signal)
      .then((result) => {
        setKnowledge(result)
        setError(null)
      })
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setError(reason instanceof Error ? reason.message : 'Company KB non disponibile')
      })
      .finally(() => {
        if (!controller.signal.aborted) setKnowledgeLoading(false)
      })
    return () => controller.abort()
  }, [])

  async function refreshKnowledge() {
    const result = await api.globalKnowledge()
    setKnowledge(result)
  }

  async function uploadDocument(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file || uploading) return
    setUploading(true)
    setFeedback(null)
    setError(null)
    try {
      const document = await api.uploadGlobalKnowledgeFile(file)
      await refreshKnowledge()
      setFeedback(`${document.name} indicizzato in ${document.chunk_count} frammenti.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Caricamento non riuscito')
    } finally {
      setUploading(false)
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
      setFeedback(`${name} rimosso dalla Company KB.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Rimozione non riuscita')
    } finally {
      setDeletingId(null)
    }
  }

  return (
    <AppShell active="settings">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="settings-page page-container">
        <header className="page-heading">
          <h1>Impostazioni generali</h1>
          <p>Preferenze valide per tutta l'applicazione e per tutti i progetti</p>
        </header>

        <section className="settings-card general-card">
          <h2>Applicazione</h2>
          <p>Configura il comportamento predefinito di Mapi RAG.</p>
          <div className="settings-card-divider" />
          <div className="settings-row">
            <div><strong>Modello predefinito</strong><span>Utilizzato nelle nuove conversazioni</span></div>
            <button className="value-control" type="button">Mapi RAG</button>
          </div>
          <div className="settings-row">
            <strong>Lingua predefinita</strong>
            <span>Italiano</span>
          </div>
        </section>

        <section className="settings-card general-card global-knowledge-card">
          <div className="global-knowledge-heading">
            <div>
              <h2>Conoscenza globale</h2>
              <p>Fonti condivise e dati aziendali disponibili per i progetti.</p>
            </div>
            <input
              ref={fileInput}
              className="source-file-input"
              type="file"
              accept=".pdf,.txt,application/pdf,text/plain"
              onChange={uploadDocument}
            />
            <button
              className="button button--compact global-upload-button"
              type="button"
              disabled={uploading}
              onClick={() => fileInput.current?.click()}
            >
              {uploading ? <LoaderCircle className="spin" size={15} /> : <Upload size={15} />}
              {uploading ? 'Indicizzazione' : 'Carica documento'}
            </button>
          </div>
          <div className="settings-card-divider" />

          <div className="linked-source-grid global-source-grid">
            <div className="linked-source linked-source--status">
              <div><strong>General KB</strong><span>Norme e materiali trasversali</span></div>
              <StatusPill tone="info">Markdown</StatusPill>
            </div>
            <div className="linked-source linked-source--status">
              <div><strong>Company KB</strong><span>Documenti, referenze e certificazioni</span></div>
              <StatusPill tone={documentCount ? 'success' : 'info'}>
                {documentCountLabel}
              </StatusPill>
            </div>
            <div className="linked-source linked-source--status">
              <div><strong>Company Facts</strong><span>Mapi Ingegneria S.r.l.</span></div>
              <StatusPill tone="success">{knowledge?.company_fact_count ?? 0} verificati</StatusPill>
            </div>
          </div>

          <div className="company-kb-section">
            <div className="setting-section-title">
              <span>Documenti Company KB</span>
              {knowledge && (
                <small>{knowledge.chunk_count} frammenti indicizzati una sola volta</small>
              )}
            </div>
            {knowledgeLoading ? (
              <LoadingState label="Caricamento Company KB" />
            ) : knowledge?.documents.length ? (
              <div className="company-document-list">
                {knowledge.documents.map((document) => (
                  <div className="company-document-row" key={document.id}>
                    <FileText size={17} />
                    <div>
                      <strong>{document.name}</strong>
                      <span>{document.metadata}</span>
                    </div>
                    <StatusPill tone="success">{document.status}</StatusPill>
                    <button
                      className="icon-button company-document-delete"
                      type="button"
                      title={`Rimuovi ${document.name}`}
                      aria-label={`Rimuovi ${document.name}`}
                      disabled={deletingId !== null}
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
                <span>Nessun documento aziendale caricato.</span>
              </div>
            )}
            {feedback && <p className="upload-feedback upload-feedback--success" aria-live="polite">{feedback}</p>}
            {error && <p className="upload-feedback upload-feedback--error" role="alert">{error}</p>}
          </div>
        </section>

        <section className="settings-card general-card review-setting">
          <div>
            <h2>Revisione e provenienza</h2>
            <p>Regole applicate alla generazione dei documenti.</p>
          </div>
          <div className="settings-card-divider" />
          <div className="settings-row">
            <strong>Richiedi conferma umana prima dell'esportazione</strong>
            <button
              type="button"
              role="switch"
              aria-checked={reviewRequired}
              className={`toggle${reviewRequired ? ' is-on' : ''}`}
              onClick={() => setReviewRequired((value) => !value)}
            >
              <span />
            </button>
          </div>
        </section>
      </div>
    </AppShell>
  )
}
