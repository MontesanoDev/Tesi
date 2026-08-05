import { LoaderCircle } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import { useProject } from '../hooks/useProject'
import type { ProjectGlobalKnowledgeDocument } from '../types'

export function ProjectSettingsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { project, loading, error } = useProject(projectId)
  const [globalDocuments, setGlobalDocuments] = useState<ProjectGlobalKnowledgeDocument[]>([])
  const [globalLoading, setGlobalLoading] = useState(true)
  const [globalError, setGlobalError] = useState<string | null>(null)
  const [linkingId, setLinkingId] = useState<number | null>(null)

  useEffect(() => {
    if (!projectId) return
    const controller = new AbortController()
    setGlobalLoading(true)
    api.projectGlobalKnowledge(projectId, controller.signal)
      .then((documents) => {
        setGlobalDocuments(documents)
        setGlobalError(null)
      })
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setGlobalError(reason instanceof Error ? reason.message : 'Company KB non disponibile')
      })
      .finally(() => {
        if (!controller.signal.aborted) setGlobalLoading(false)
      })
    return () => controller.abort()
  }, [projectId])

  if (loading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (error || !project) {
    return <AppShell active="projects"><ErrorState message={error ?? 'Progetto non trovato'} /></AppShell>
  }

  const activeProjectId = project.id
  const linkedDocumentCount = globalDocuments.filter((document) => document.linked).length
  const linkedDocumentLabel = linkedDocumentCount === 1
    ? '1 documento'
    : `${linkedDocumentCount} documenti`

  async function toggleGlobalDocument(document: ProjectGlobalKnowledgeDocument) {
    if (linkingId !== null) return
    setLinkingId(document.id)
    setGlobalError(null)
    try {
      const updated = await api.updateProjectGlobalKnowledge(
        activeProjectId,
        document.id,
        !document.linked,
      )
      setGlobalDocuments((current) => current.map((item) => (
        item.id === updated.id ? updated : item
      )))
    } catch (reason) {
      setGlobalError(reason instanceof Error ? reason.message : 'Collegamento non riuscito')
    } finally {
      setLinkingId(null)
    }
  }

  return (
    <AppShell active="projects" project={project}>
      <button className="back-link" type="button" onClick={() => navigate(`/projects/${project.id}`)}>
        ← {project.title}
      </button>
      <div className="settings-page page-container settings-page--project">
        <header className="page-heading">
          <h1>Impostazioni progetto</h1>
          <p>Configura le conoscenze utilizzate da Mapi RAG in questo progetto</p>
        </header>

        <section className="settings-card project-setting-card">
          <div className="settings-card-heading">
            <span className="setting-monogram setting-monogram--blue">KB</span>
            <div>
              <h2>Conoscenza condivisa</h2>
              <p>Fonti globali rese disponibili nel progetto corrente</p>
            </div>
            <StatusPill tone={linkedDocumentCount ? 'success' : 'info'}>
              {linkedDocumentLabel}
            </StatusPill>
          </div>
          <div className="settings-card-divider" />
          <div className="setting-section-title">
            <span>Fonti collegate</span>
            <button
              className="button button--compact"
              type="button"
              onClick={() => navigate(`/projects/${project.id}/knowledge`)}
            >
              Apri artefatti Markdown
            </button>
          </div>
          <div className="linked-source-grid">
            <div className="linked-source">
              <strong>General KB</strong>
              <span>Norme e materiali tecnici</span>
            </div>
            <div className="linked-source">
              <strong>Company Facts</strong>
              <span>Mapi Ingegneria · dati strutturati verificati</span>
            </div>
          </div>
          <div className="company-kb-project-section">
            <div className="setting-section-title">
              <span>Documenti Company KB</span>
              <button
                className="button button--compact"
                type="button"
                onClick={() => navigate('/settings')}
              >
                Gestisci archivio globale
              </button>
            </div>
            {globalLoading ? (
              <LoadingState label="Caricamento Company KB" />
            ) : globalDocuments.length ? (
              <div className="project-global-document-list">
                {globalDocuments.map((document) => (
                  <div className="project-global-document-row" key={document.id}>
                    <div>
                      <strong>{document.name}</strong>
                      <span>{document.metadata}</span>
                    </div>
                    {linkingId === document.id && <LoaderCircle className="spin" size={16} />}
                    <button
                      type="button"
                      role="switch"
                      aria-label={`Collega ${document.name}`}
                      aria-checked={document.linked}
                      className={`toggle${document.linked ? ' is-on' : ''}`}
                      disabled={linkingId !== null}
                      onClick={() => toggleGlobalDocument(document)}
                    >
                      <span />
                    </button>
                  </div>
                ))}
              </div>
            ) : (
              <p className="project-global-empty">
                Nessun documento aziendale disponibile nell'archivio globale.
              </p>
            )}
            {globalError && <p className="upload-feedback upload-feedback--error" role="alert">{globalError}</p>}
          </div>
        </section>

        <section className="settings-card project-setting-card call-facts-card">
          <div className="settings-card-heading">
            <span className="setting-monogram setting-monogram--gold">CF</span>
            <div>
              <h2>Call Facts</h2>
              <p>Fatti estratti dalle fonti e sottoposti a verifica umana</p>
            </div>
            <StatusPill tone="warning">Progetto</StatusPill>
          </div>
          <div className="settings-card-divider" />
          <span className="section-label">Fonti del progetto</span>
          <div className="call-document-row">
            <div>
              <strong>{project.files.find((file) => file.kind === 'source')?.name ?? 'Nessun bando collegato'}</strong>
              <span>{project.call_fact_count} fatti estratti · ultima estrazione oggi</span>
            </div>
            <StatusPill tone="warning">{project.missing_fact_count} mancanti</StatusPill>
          </div>
          <div className="metric-grid">
            <div><strong>{project.call_fact_count}</strong><span>Call facts</span></div>
            <div><strong>{project.model_count}</strong><span>Template</span></div>
            <div><strong>{project.missing_fact_count}</strong><span>Dato mancante</span></div>
            <button className="button" type="button" onClick={() => navigate(`/projects/${project.id}/knowledge`)}>
              Apri Call Facts
            </button>
          </div>
        </section>

        <div className="scope-banner">
          <strong>Scope controllato</strong>
          <span>I documenti aziendali sono condivisi solo se collegati; i Call Facts restano isolati nel progetto corrente.</span>
        </div>
      </div>
    </AppShell>
  )
}
