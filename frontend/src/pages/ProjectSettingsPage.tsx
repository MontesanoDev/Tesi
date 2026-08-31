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

  const sourceFiles = project.files.filter((file) => file.kind === 'source')
  const sourceSummary = sourceFiles.length === 0
    ? 'Nessuna fonte indicizzata'
    : sourceFiles.length === 1
      ? sourceFiles[0].name
      : `${sourceFiles[0].name} e altre ${sourceFiles.length - 1} fonti`

  return (
    <AppShell active="projects" project={project}>
      <button
        className="back-link"
        type="button"
        onClick={() => navigate(`/projects/${project.id}`)}
      >
        ← {project.title}
      </button>
      <div className="settings-page page-container settings-page--project">
        <header className="page-heading">
          <h1>Impostazioni progetto</h1>
          <p>Gestisci i fatti estratti dalle fonti del progetto</p>
        </header>

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
              <strong>{sourceSummary}</strong>
              <span>
                {sourceFiles.length} {sourceFiles.length === 1 ? 'fonte indicizzata' : 'fonti indicizzate'}
              </span>
            </div>
            <StatusPill tone={project.missing_fact_count > 0 ? 'warning' : 'success'}>
              {project.missing_fact_count} mancanti
            </StatusPill>
          </div>
          <div className="metric-grid">
            <div><strong>{project.call_fact_count}</strong><span>Call Facts</span></div>
            <div><strong>{sourceFiles.length}</strong><span>Fonti</span></div>
            <div><strong>{project.missing_fact_count}</strong><span>Dati mancanti</span></div>
            <button
              className="button"
              type="button"
              onClick={() => navigate(`/projects/${project.id}/knowledge`)}
            >
              Apri Call Facts
            </button>
          </div>
        </section>
      </div>
    </AppShell>
  )
}
