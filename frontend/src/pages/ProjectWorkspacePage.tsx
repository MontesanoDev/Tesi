import {
  ArrowUp,
  ChevronDown,
  EllipsisVertical,
  FileText,
  LoaderCircle,
  Trash2,
  X,
} from 'lucide-react'
import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { ProjectKnowledgePanel } from '../components/ProjectKnowledgePanel'
import { ProjectKnowledgeSummary } from '../components/ProjectKnowledgeSummary'
import { useDismissibleMenu } from '../hooks/useDismissibleMenu'
import { useProject } from '../hooks/useProject'
import type { GroundedAnswer } from '../types'

interface ChatTurn {
  id: string
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
  const { projectId, conversationId } = useParams()
  const navigate = useNavigate()
  const { project, loading, error, refresh } = useProject(projectId)
  const [menuOpen, setMenuOpen] = useState(false)
  const [renameDialogOpen, setRenameDialogOpen] = useState(false)
  const [renameTitle, setRenameTitle] = useState('')
  const [renamingProject, setRenamingProject] = useState(false)
  const [renameError, setRenameError] = useState<string | null>(null)
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false)
  const [deletingProject, setDeletingProject] = useState(false)
  const [deleteError, setDeleteError] = useState<string | null>(null)
  const [prompt, setPrompt] = useState('')
  const [turns, setTurns] = useState<ChatTurn[]>([])
  const [searching, setSearching] = useState(false)
  const [conversationLoading, setConversationLoading] = useState(false)
  const [conversationError, setConversationError] = useState<string | null>(null)
  const turnSequence = useRef(0)
  const chatThread = useRef<HTMLDivElement>(null)
  const activeConversation = useRef<string | null>(conversationId ?? null)
  const loadedConversation = useRef<string | null>(null)
  const projectMenuRef = useDismissibleMenu<HTMLDivElement>(
    menuOpen,
    () => setMenuOpen(false),
  )

  useEffect(() => {
    setPrompt('')
    setTurns([])
    setSearching(false)
    setConversationError(null)
    turnSequence.current = 0
    activeConversation.current = null
    loadedConversation.current = null
  }, [projectId])

  useEffect(() => {
    if (!projectId) return
    if (!conversationId) {
      activeConversation.current = null
      loadedConversation.current = null
      setTurns([])
      setConversationLoading(false)
      setConversationError(null)
      return
    }
    if (loadedConversation.current === conversationId) return

    const controller = new AbortController()
    activeConversation.current = conversationId
    setTurns([])
    setConversationLoading(true)
    setConversationError(null)
    api.conversation(projectId, conversationId, controller.signal)
      .then((conversation) => {
        activeConversation.current = conversation.id
        loadedConversation.current = conversation.id
        setTurns(conversation.turns.map((turn) => ({
          id: `turn-${turn.id}`,
          question: turn.question,
          result: {
            ...turn,
            conversation_id: conversation.id,
            turn_id: turn.id,
          },
          error: null,
        })))
      })
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setConversationError(
          reason instanceof Error ? reason.message : 'Conversazione non disponibile',
        )
      })
      .finally(() => {
        if (!controller.signal.aborted) setConversationLoading(false)
      })

    return () => controller.abort()
  }, [projectId, conversationId])

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
  const activeProjectTitle = project.title

  async function submitPrompt(event: FormEvent) {
    event.preventDefault()
    const query = prompt.trim()
    if (!query || searching || conversationLoading) return
    const turnId = `local-${++turnSequence.current}`
    setTurns((current) => [
      ...current,
      { id: turnId, question: query, result: null, error: null },
    ])
    setPrompt('')
    setSearching(true)
    try {
      const result = await api.projectAnswer(
        activeProjectId,
        query,
        activeConversation.current,
      )
      activeConversation.current = result.conversation_id
      loadedConversation.current = result.conversation_id
      setTurns((current) => current.map((turn) => (
        turn.id === turnId
          ? { ...turn, id: `turn-${result.turn_id}`, result }
          : turn
      )))
      if (conversationId !== result.conversation_id) {
        navigate(
          `/projects/${activeProjectId}/conversations/${result.conversation_id}`,
          { replace: true },
        )
      }
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

  async function deleteCurrentProject() {
    if (deletingProject) return
    setDeletingProject(true)
    setDeleteError(null)
    try {
      await api.deleteProject(activeProjectId)
      navigate('/projects', { replace: true })
    } catch (reason) {
      setDeleteError(reason instanceof Error ? reason.message : 'Eliminazione non riuscita')
      setDeletingProject(false)
    }
  }

  function openRenameDialog() {
    setMenuOpen(false)
    setRenameTitle(activeProjectTitle)
    setRenameError(null)
    setRenameDialogOpen(true)
  }

  function closeRenameDialog() {
    if (renamingProject) return
    setRenameDialogOpen(false)
    setRenameError(null)
  }

  async function renameCurrentProject(event: FormEvent) {
    event.preventDefault()
    const title = renameTitle.trim()
    if (renamingProject) return
    if (title.length < 3) {
      setRenameError('Inserisci un nome di almeno 3 caratteri')
      return
    }
    if (title === activeProjectTitle) {
      closeRenameDialog()
      return
    }

    setRenamingProject(true)
    setRenameError(null)
    try {
      await api.updateProject(activeProjectId, { title })
      await refresh()
      setRenameDialogOpen(false)
    } catch (reason) {
      setRenameError(reason instanceof Error ? reason.message : 'Rinomina non riuscita')
    } finally {
      setRenamingProject(false)
    }
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
        <button
          className="send-button"
          type="submit"
          aria-label="Invia"
          disabled={!prompt.trim() || searching || conversationLoading}
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
            <div className="project-menu-wrap" ref={projectMenuRef}>
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
                  <button type="button" onClick={openRenameDialog}>Rinomina progetto</button>
                  <button
                    className="danger-command"
                    type="button"
                    onClick={() => {
                      setMenuOpen(false)
                      setDeleteError(null)
                      setDeleteDialogOpen(true)
                    }}
                  >
                    Elimina progetto <Trash2 size={16} />
                  </button>
                </div>
              )}
            </div>
          </header>

          {conversationLoading ? (
            <LoadingState label="Caricamento conversazione" />
          ) : conversationError ? (
            <ErrorState message={conversationError} />
          ) : turns.length === 0 ? (
            <>
              {composer}
              <ProjectKnowledgeSummary project={project} />

              {!conversationId && (
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
                            return
                          }
                          navigate(
                            `/projects/${project.id}/conversations/${conversation.id}`,
                          )
                        }}
                      >
                        <strong>{conversation.title}</strong>
                        <span>{conversation.metadata}</span>
                      </button>
                    ))}
                  </div>
                </section>
              )}
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

      {renameDialogOpen && (
        <div className="modal-layer" role="presentation">
          <button
            className="modal-scrim"
            type="button"
            aria-label="Chiudi rinomina progetto"
            disabled={renamingProject}
            onClick={closeRenameDialog}
          />
          <form
            className="project-modal rename-project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="rename-project-title"
            noValidate
            onSubmit={renameCurrentProject}
          >
            <div className="modal-heading">
              <h2 id="rename-project-title">Rinomina progetto</h2>
              <button
                className="icon-button"
                type="button"
                aria-label="Chiudi"
                disabled={renamingProject}
                onClick={closeRenameDialog}
              >
                <X size={18} />
              </button>
            </div>
            <label>
              Nome del progetto
              <input
                required
                minLength={3}
                maxLength={120}
                autoFocus
                value={renameTitle}
                onChange={(event) => {
                  setRenameTitle(event.target.value)
                  setRenameError(null)
                }}
              />
            </label>
            {renameError && (
              <p className="upload-feedback upload-feedback--error" role="alert">
                {renameError}
              </p>
            )}
            <div className="modal-actions">
              <button
                className="button"
                type="button"
                disabled={renamingProject}
                onClick={closeRenameDialog}
              >
                Annulla
              </button>
              <button
                className="button button--primary"
                type="submit"
                disabled={!renameTitle.trim() || renamingProject}
              >
                {renamingProject && <LoaderCircle className="spin" size={15} />}
                Salva nome
              </button>
            </div>
          </form>
        </div>
      )}

      {deleteDialogOpen && (
        <div className="modal-layer" role="presentation">
          <button
            className="modal-scrim"
            type="button"
            aria-label="Chiudi conferma eliminazione"
            disabled={deletingProject}
            onClick={() => setDeleteDialogOpen(false)}
          />
          <section
            className="project-modal delete-project-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="delete-project-title"
          >
            <div className="modal-heading">
              <h2 id="delete-project-title">Elimina progetto</h2>
              <button
                className="icon-button"
                type="button"
                aria-label="Chiudi"
                disabled={deletingProject}
                onClick={() => setDeleteDialogOpen(false)}
              >
                <X size={18} />
              </button>
            </div>
            <p>
              Stai per eliminare <strong>{project.title}</strong> insieme a conversazioni,
              documenti e artefatti locali.
            </p>
            <p className="delete-project-note">
              La conoscenza globale dell'azienda non verrà eliminata. Questa operazione non è annullabile.
            </p>
            {deleteError && <p className="upload-feedback upload-feedback--error" role="alert">{deleteError}</p>}
            <div className="modal-actions">
              <button
                className="button"
                type="button"
                disabled={deletingProject}
                onClick={() => setDeleteDialogOpen(false)}
              >
                Annulla
              </button>
              <button
                className="button button--danger"
                type="button"
                autoFocus
                disabled={deletingProject}
                onClick={deleteCurrentProject}
              >
                {deletingProject ? <LoaderCircle className="spin" size={16} /> : <Trash2 size={16} />}
                {deletingProject ? 'Eliminazione' : 'Elimina definitivamente'}
              </button>
            </div>
          </section>
        </div>
      )}
    </AppShell>
  )
}
