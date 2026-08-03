import { useNavigate, useParams } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import { useProject } from '../hooks/useProject'

export function ProjectSettingsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { project, loading, error } = useProject(projectId)

  if (loading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (error || !project) {
    return <AppShell active="projects"><ErrorState message={error ?? 'Progetto non trovato'} /></AppShell>
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
            <StatusPill tone="info">Collegata</StatusPill>
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
              <span>Mapi Ingegneria · 28 dati verificati</span>
            </div>
          </div>
        </section>

        <section className="settings-card project-setting-card call-facts-card">
          <div className="settings-card-heading">
            <span className="setting-monogram setting-monogram--gold">CF</span>
            <div>
              <h2>Call Facts</h2>
              <p>Fatti estratti e verificati dal bando del progetto corrente</p>
            </div>
            <StatusPill tone="warning">Progetto</StatusPill>
          </div>
          <div className="settings-card-divider" />
          <span className="section-label">Documento del bando</span>
          <div className="call-document-row">
            <div>
              <strong>{project.files.find((file) => file.kind === 'source')?.name ?? 'Nessun bando collegato'}</strong>
              <span>{project.call_fact_count} fatti verificati · ultima estrazione oggi</span>
            </div>
            <StatusPill tone="warning">{project.missing_fact_count} da verificare</StatusPill>
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
          <span>La Knowledge Base è condivisa; i Call Facts restano isolati nel progetto corrente.</span>
        </div>
      </div>
    </AppShell>
  )
}
