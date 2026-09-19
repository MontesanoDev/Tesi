import { Search, X } from 'lucide-react'
import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import type { ProjectSummary } from '../types'

export function ProjectsPage() {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<ProjectSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')
  const [sortOrder, setSortOrder] = useState<'updated' | 'name'>('updated')
  const [modalOpen, setModalOpen] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    api
      .projects(controller.signal)
      .then(setProjects)
      .catch((reason: Error) => {
        if (reason.name !== 'AbortError') setError(reason.message)
      })
      .finally(() => setLoading(false))
    return () => controller.abort()
  }, [])

  const filtered = projects.filter((project) =>
    `${project.title} ${project.description}`.toLowerCase().includes(query.toLowerCase()),
  )
  // The API returns projects in most-recently-updated order.
  if (sortOrder === 'name') {
    filtered.sort((a, b) => a.title.localeCompare(b.title, 'it', {
      sensitivity: 'base', numeric: true,
    }))
  }

  async function createProject(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const form = new FormData(event.currentTarget)
    const created = await api.createProject({
      title: String(form.get('title')),
      description: String(form.get('description')),
    })
    setModalOpen(false)
    navigate(`/projects/${created.id}`)
  }

  return (
    <AppShell active="projects" contentClassName="projects-content">
      <div className="projects-page page-container">
        <header className="projects-header">
          <h1>Progetti</h1>
          <div className="projects-actions">
            <label className="search-control">
              <Search size={17} />
              <input
                aria-label="Cerca progetti"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Cerca"
              />
            </label>
            <label className="sort-control">
              <span>Ordina per</span>
              <select value={sortOrder} aria-label="Ordina progetti"
                onChange={(event) => setSortOrder(event.target.value as 'updated' | 'name')}>
                <option value="updated">Ultimo aggiornamento</option>
                <option value="name">Nome</option>
              </select>
            </label>
            <button className="button button--primary" onClick={() => setModalOpen(true)}>
              Nuovo progetto
            </button>
          </div>
        </header>

        {loading ? (
          <LoadingState label="Caricamento progetti" />
        ) : error ? (
          <ErrorState message={error} />
        ) : (
          <>
            <span className="section-label">{filtered.length} progetti</span>
            <div className="project-grid">
              {filtered.map((project) => (
                <button
                  className="project-card"
                  key={project.id}
                  type="button"
                  onClick={() => navigate(`/projects/${project.id}`)}
                >
                  <strong>{project.title}</strong>
                  <p>{project.description}</p>
                  <div className="project-card-footer">
                    <span>
                      {project.source_count} fonti · {project.model_count} modelli
                      <small>{project.updated_label}</small>
                    </span>
                    <StatusPill tone={project.status_tone}>{project.status}</StatusPill>
                  </div>
                </button>
              ))}
            </div>
          </>
        )}
      </div>

      {modalOpen && (
        <div className="modal-layer" role="presentation">
          <button
            className="modal-scrim"
            type="button"
            aria-label="Chiudi finestra"
            onClick={() => setModalOpen(false)}
          />
          <form className="project-modal" onSubmit={createProject}>
            <div className="modal-heading">
              <h2>Crea un progetto</h2>
              <button
                className="icon-button"
                type="button"
                aria-label="Chiudi"
                onClick={() => setModalOpen(false)}
              >
                <X size={18} />
              </button>
            </div>
            <label>
              Nome del progetto
              <input name="title" required minLength={3} autoFocus />
            </label>
            <label>
              Obiettivo
              <textarea name="description" required minLength={3} rows={4} />
            </label>
            <div className="modal-actions">
              <button className="button" type="button" onClick={() => setModalOpen(false)}>
                Annulla
              </button>
              <button className="button button--primary" type="submit">
                Crea progetto
              </button>
            </div>
          </form>
        </div>
      )}
    </AppShell>
  )
}
