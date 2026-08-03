import { ArrowUp, ChevronDown, EllipsisVertical, FileText, Paperclip } from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { ProjectKnowledgePanel } from '../components/ProjectKnowledgePanel'
import { useProject } from '../hooks/useProject'
import type { GroundedAnswer } from '../types'

interface ChatTurn {
  id: number
  question: string
  result: GroundedAnswer | null
  error: string | null
}

function turnStatus(turn: ChatTurn) {
  if (turn.error) return turn.error
  if (!turn.result) return 'Ricerca delle evidenze nelle fonti del progetto...'
  if (turn.result.generation_status === 'direct') return 'Risposta diretta di Mapi RAG.'
  if (turn.result.generation_status === 'completed') {
    return turn.result.evidence.length === 1
      ? 'Risposta generata da 1 evidenza del progetto.'
      : `Risposta generata da ${turn.result.evidence.length} evidenze del progetto.`
  }
  return turn.result.notice ?? 'Nessuna evidenza pertinente trovata nelle fonti indicizzate.'
}

function ConversationTurn({ turn }: { turn: ChatTurn }) {
  const result = turn.result
  const evidence = result?.evidence ?? []
  const answerTitleId = `answer-title-${turn.id}`
  const evidenceTitleId = `evidence-title-${turn.id}`
  const activityClass = turn.error
    ? 'activity-dot activity-dot--error'
    : result
      ? 'activity-dot activity-dot--done'
      : 'activity-dot'

  return (
    <article className="chat-turn">
      <div className="user-message">
        <span>Tu</span>
        <p>{turn.question}</p>
      </div>

      <div className="turn-status" aria-live="polite">
        <span className={activityClass} />
        <p>{turnStatus(turn)}</p>
      </div>

      {result?.answer && (
        <section className="grounded-answer" aria-labelledby={answerTitleId}>
          <div className="grounded-answer-heading">
            <h2 id={answerTitleId}>Risposta Mapi</h2>
            {result.model && <span>{result.model}</span>}
          </div>
          <p>{result.answer}</p>
          {result.missing_information.length > 0 && (
            <div className="missing-information">
              <strong>Informazioni mancanti</strong>
              <ul>
                {result.missing_information.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </section>
      )}

      {evidence.length > 0 && (
        <details className="evidence-results" aria-labelledby={evidenceTitleId}>
          <summary className="evidence-heading">
            <span>
              <ChevronDown size={15} />
              <span className="section-label" id={evidenceTitleId}>Evidenze recuperate</span>
            </span>
            <span>{evidence.length} risultati</span>
          </summary>
          <ol className="evidence-list">
            {evidence.map((item, index) => (
              <li
                className={`evidence-item${result?.citations.includes(index + 1) ? ' is-cited' : ''}`}
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
        </details>
      )}
    </article>
  )
}

export function ProjectWorkspacePage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { project, loading, error, refresh } = useProject(projectId)
  const [menuOpen, setMenuOpen] = useState(false)
  const [prompt, setPrompt] = useState('')
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [searching, setSearching] = useState(false)
  const turnSequence = useRef(0)
  const chatThread = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setPrompt('')
    setTurns([])
    setSearching(false)
    turnSequence.current = 0
  }, [projectId])

  useEffect(() => {
    const thread = chatThread.current
    if (!thread) return
    const frame = requestAnimationFrame(() => {
      thread.scrollTo({ top: thread.scrollHeight, behavior: 'smooth' })
    })
    return () => cancelAnimationFrame(frame)
  }, [turns])

  if (loading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (error || !project) {
    return <AppShell active="projects"><ErrorState message={error ?? 'Progetto non trovato'} /></AppShell>
  }
  const activeProjectId = project.id

  async function submitPrompt(event: FormEvent) {
    event.preventDefault()
    const query = prompt.trim()
    if (!query || searching) return
    const turnId = ++turnSequence.current
    setTurns((current) => [
      ...current,
      { id: turnId, question: query, result: null, error: null },
    ])
    setPrompt('')
    setSearching(true)
    try {
      const result = await api.projectAnswer(activeProjectId, query)
      setTurns((current) => current.map((turn) => (
        turn.id === turnId ? { ...turn, result } : turn
      )))
    } catch (reason) {
      const message = reason instanceof Error ? reason.message : 'Ricerca non riuscita'
      setTurns((current) => current.map((turn) => (
        turn.id === turnId ? { ...turn, error: message } : turn
      )))
    } finally {
      setSearching(false)
    }
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return
    event.preventDefault()
    event.currentTarget.form?.requestSubmit()
  }

  const composer = (
    <form
      className={`composer${turns.length > 0 ? ' composer--docked' : ''}`}
      onSubmit={submitPrompt}
    >
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
  )

  return (
    <AppShell active="projects" project={project} contentClassName="workspace-content">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="workspace-layout">
        <section className={`workspace-main${turns.length > 0 ? ' workspace-main--conversation' : ''}`}>
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

          {turns.length === 0 ? (
            <>
              {composer}
              <div className="assistant-note">
                <span className="activity-dot activity-dot--idle" />
                <p>Mapi RAG usa i documenti, i dati aziendali e i modelli collegati a questo progetto.</p>
              </div>

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
            </>
          ) : (
            <>
              <div className="chat-thread" ref={chatThread}>
                {turns.map((turn) => (
                  <div key={turn.id}>
                    <ConversationTurn turn={turn} />
                  </div>
                ))}
              </div>
              {composer}
            </>
          )}
        </section>

        <ProjectKnowledgePanel project={project} onProjectChange={refresh} />
      </div>
    </AppShell>
  )
}
