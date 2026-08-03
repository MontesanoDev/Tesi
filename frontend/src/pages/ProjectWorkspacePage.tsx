import { ArrowUp, EllipsisVertical, FileText, Paperclip } from 'lucide-react'
import { useState, type FormEvent, type KeyboardEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { ProjectKnowledgePanel } from '../components/ProjectKnowledgePanel'
import { useProject } from '../hooks/useProject'
import type { GroundedAnswer } from '../types'

export function ProjectWorkspacePage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { project, loading, error, refresh } = useProject(projectId)
  const [menuOpen, setMenuOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [savedPrompt, setSavedPrompt] = useState<string | null>(null)
  const [answerResult, setAnswerResult] = useState<GroundedAnswer | null>(null)
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const evidence = answerResult?.evidence ?? []

  if (loading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (error || !project) {
    return <AppShell active="projects"><ErrorState message={error ?? 'Progetto non trovato'} /></AppShell>
  }
  const activeProjectId = project.id

  async function submitPrompt(event: FormEvent) {
    event.preventDefault()
    const query = prompt.trim()
    if (!query || searching) return
    setSavedPrompt(query)
    setPrompt('')
    setAnswerResult(null)
    setSearchError(null)
    setSearching(true)
    try {
      const result = await api.projectAnswer(activeProjectId, query)
      setAnswerResult(result)
    } catch (reason) {
      setSearchError(reason instanceof Error ? reason.message : 'Ricerca non riuscita')
    } finally {
      setSearching(false)
    }
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return
    event.preventDefault()
    event.currentTarget.form?.requestSubmit()
  }

  return (
    <AppShell active="projects" project={project} contentClassName="workspace-content">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="workspace-layout">
        <section className="workspace-main">
          <header className="project-heading">
            <div>
              <h1>{project.title}</h1>
              <p>{project.description}</p>
            </div>
            <div className="project-menu-wrap">
              <button
                className={`icon-button project-menu-trigger${menuOpen ? ' is-active' : ''}`}
                type="button"
                aria-label="Menu progetto"
                aria-expanded={menuOpen}
                onClick={() => setMenuOpen((value) => !value)}
              >
                <EllipsisVertical size={21} />
              </button>
              {menuOpen && (
                <div className="project-menu">
                  <button
                    type="button"
                    onClick={() => navigate(`/projects/${project.id}/settings`)}
                  >
                    Impostazioni progetto <span>→</span>
                  </button>
                  <div />
                  <button type="button">Rinomina progetto</button>
                  <button className="muted-command" type="button">Archivia progetto</button>
                </div>
              )}
            </div>
          </header>

          <form className="composer" onSubmit={submitPrompt}>
            <textarea
              aria-label="Messaggio per Mapi RAG"
              placeholder="Come posso aiutarti in questo progetto?"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              onKeyDown={handleComposerKeyDown}
            />
            <div className="composer-tools">
              <button className="icon-button" type="button" aria-label="Allega file">
                <Paperclip size={19} />
              </button>
              <span className="composer-chip">Fonti del progetto</span>
              <span className="composer-chip">Mapi RAG</span>
              <button
                className="send-button"
                type="submit"
                aria-label="Invia"
                disabled={!prompt.trim() || searching}
              >
                <ArrowUp size={20} />
              </button>
            </div>
          </form>

          <div className="assistant-note" aria-live="polite">
            <span
              className={savedPrompt && !searching ? 'activity-dot activity-dot--done' : 'activity-dot'}
            />
            <p>
              {searching
                ? 'Ricerca delle evidenze nelle fonti del progetto...'
                : searchError
                  ? searchError
                  : answerResult?.generation_status === 'completed'
                    ? evidence.length === 1
                      ? 'Risposta generata da 1 evidenza del progetto.'
                      : `Risposta generata da ${evidence.length} evidenze del progetto.`
                    : answerResult?.notice
                      ? answerResult.notice
                      : savedPrompt
                        ? 'Nessuna evidenza pertinente trovata nelle fonti indicizzate.'
                      : 'Mapi RAG usa i documenti, i dati aziendali e i modelli collegati a questo progetto.'}
            </p>
          </div>

          {answerResult?.answer && (
            <section className="grounded-answer" aria-labelledby="answer-title">
              <div className="grounded-answer-heading">
                <h2 id="answer-title">Risposta Mapi</h2>
                {answerResult.model && <span>{answerResult.model}</span>}
              </div>
              <p>{answerResult.answer}</p>
              {answerResult.missing_information.length > 0 && (
                <div className="missing-information">
                  <strong>Informazioni mancanti</strong>
                  <ul>
                    {answerResult.missing_information.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              )}
            </section>
          )}

          {evidence.length > 0 && (
            <section className="evidence-results" aria-labelledby="evidence-title">
              <div className="evidence-heading">
                <span className="section-label" id="evidence-title">Evidenze recuperate</span>
                <span>{evidence.length} risultati</span>
              </div>
              <ol className="evidence-list">
                {evidence.map((item, index) => (
                  <li
                    className={`evidence-item${answerResult?.citations.includes(index + 1) ? ' is-cited' : ''}`}
                    key={item.chunk_id}
                  >
                    <div className="evidence-source">
                      <span className="evidence-reference">[{index + 1}]</span>
                      <FileText size={15} />
                      <strong>{item.source_name}</strong>
                      <span className="evidence-fragment">Frammento {item.chunk_index + 1}</span>
                    </div>
                    <p>{item.excerpt}</p>
                  </li>
                ))}
              </ol>
            </section>
          )}

          <section className="recent-conversations">
            <span className="section-label">Conversazioni recenti</span>
            <div className="conversation-grid">
              {project.conversations.map((conversation) => (
                <button
                  className="conversation-item"
                  type="button"
                  key={conversation.id}
                  onClick={() => {
                    if (conversation.target === 'review') {
                      navigate(`/projects/${project.id}/review`)
                    }
                  }}
                >
                  <strong>{conversation.title}</strong>
                  <span>{conversation.metadata}</span>
                </button>
              ))}
            </div>
          </section>
        </section>

        <ProjectKnowledgePanel project={project} onProjectChange={refresh} />
      </div>
    </AppShell>
  )
}
