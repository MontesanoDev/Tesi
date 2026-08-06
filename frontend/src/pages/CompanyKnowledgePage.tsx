import {
  BookOpen,
  Building2,
  Database,
  FileText,
  LoaderCircle,
  Save,
  Trash2,
  Upload,
} from 'lucide-react'
import { useEffect, useRef, useState, type ChangeEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import type {
  GlobalKnowledgeOverview,
  KnowledgeArtifactDetail,
} from '../types'

type KnowledgeView = 'company' | 'facts' | 'general'

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

export function CompanyKnowledgePage() {
  const [activeView, setActiveView] = useState<KnowledgeView>('company')
  const [knowledge, setKnowledge] = useState<GlobalKnowledgeOverview | null>(null)
  const [companyFacts, setCompanyFacts] = useState<KnowledgeArtifactDetail | null>(null)
  const [factsContent, setFactsContent] = useState('')
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [savingFacts, setSavingFacts] = useState(false)
  const [deletingId, setDeletingId] = useState<number | null>(null)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const fileInput = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const controller = new AbortController()
    Promise.all([
      api.globalKnowledge(controller.signal),
      api.companyFacts(controller.signal),
    ])
      .then(([overview, facts]) => {
        setKnowledge(overview)
        setCompanyFacts(facts)
        setFactsContent(facts.content)
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
  const factsDirty = companyFacts?.content !== factsContent

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
    if (!file || uploading || activeView === 'facts') return
    setUploading(true)
    setFeedback(null)
    setError(null)
    try {
      const document = await api.uploadGlobalKnowledgeFile(file, activeView)
      await refreshKnowledge()
      setFeedback(`${document.name} aggiunto a ${viewCopy[activeView].title} in ${document.chunk_count} frammenti.`)
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
      setFeedback(`${name} rimosso dall'archivio globale.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Rimozione non riuscita')
    } finally {
      setDeletingId(null)
    }
  }

  async function saveCompanyFacts() {
    if (!factsDirty || savingFacts) return
    setSavingFacts(true)
    setFeedback(null)
    setError(null)
    try {
      const updated = await api.updateCompanyFacts(factsContent)
      setCompanyFacts(updated)
      await refreshKnowledge()
      setFeedback('Company Facts salvati e reindicizzati nei progetti.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      setSavingFacts(false)
    }
  }

  return (
    <AppShell active="company">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="settings-page company-knowledge-page page-container">
        <header className="page-heading">
          <h1>Dati aziendali e conoscenza</h1>
          <p>Gestisci le fonti globali e scegli esplicitamente il loro ruolo</p>
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
            className={activeView === 'facts' ? 'is-active' : ''}
            type="button"
            role="tab"
            aria-selected={activeView === 'facts'}
            onClick={() => selectView('facts')}
          >
            <Database size={16} /> Company Facts
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
          ) : activeView === 'facts' ? (
            <>
              <div className="global-knowledge-heading">
                <div>
                  <h2>Company Facts</h2>
                  <p>Dati aziendali strutturati e verificati. Non vengono ricavati implicitamente da un PDF.</p>
                </div>
                <StatusPill tone="success">{knowledge?.company_fact_count ?? 0} campi</StatusPill>
              </div>
              <textarea
                className="markdown-editor company-facts-editor"
                aria-label="Contenuto di Company Facts"
                value={factsContent}
                spellCheck={false}
                onChange={(event) => setFactsContent(event.target.value)}
              />
              <div className="company-facts-actions">
                <span>
                  {companyFacts ? `Versione ${companyFacts.version}` : 'Artefatto non disponibile'} ·{' '}
                  {factsDirty ? 'Modifiche non salvate' : 'Salvato'}
                </span>
                <button
                  className="button artifact-save"
                  type="button"
                  disabled={!factsDirty || savingFacts}
                  onClick={saveCompanyFacts}
                >
                  {savingFacts ? <LoaderCircle className="spin" size={15} /> : <Save size={15} />}
                  Salva
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="global-knowledge-heading">
                <div>
                  <h2>{viewCopy[activeView].title}</h2>
                  <p>{viewCopy[activeView].description}</p>
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
                  {uploading ? 'Indicizzazione' : `Carica in ${viewCopy[activeView].title}`}
                </button>
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
                  <span>{viewCopy[activeView].empty}</span>
                </div>
              )}
            </>
          )}
          {feedback && <p className="upload-feedback upload-feedback--success" aria-live="polite">{feedback}</p>}
          {error && <p className="upload-feedback upload-feedback--error" role="alert">{error}</p>}
        </section>
      </div>
    </AppShell>
  )
}
