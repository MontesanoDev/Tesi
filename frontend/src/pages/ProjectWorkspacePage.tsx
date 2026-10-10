import {
  ArrowUp,
  Plus,
  ChevronDown,
  EllipsisVertical,
  FileText,
  LoaderCircle,
  Trash2,
  X,
} from 'lucide-react'
import {
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type FormEvent,
  type KeyboardEvent,
  type ReactNode,
} from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { compilationReplyParagraphs } from '../compilationReply'
import { AppShell } from '../components/AppShell'
import { AssistantMessage } from '../components/AssistantMessage'
import { CompilationReply } from '../components/CompilationReply'
import '../components/ChatComposer.css'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { ProjectKnowledgePanel } from '../components/ProjectKnowledgePanel'
import { ProjectModelSelector } from '../components/ProjectModelSelector'
import { useDismissibleMenu } from '../hooks/useDismissibleMenu'
import { useProject } from '../hooks/useProject'
import { useCompilationSession } from '../hooks/useCompilationSession'
import type { DocumentReference, FormReference, GroundedAnswer, ProjectFile } from '../types'

interface ChatTurn {
  id: string
  question: string
  result: GroundedAnswer | null
  error: string | null
  document_reference?: DocumentReference | null
}

const MAX_PROMPT_LENGTH = 4_000

function documentReferenceOf(value: {
  document_reference?: DocumentReference | null; form_reference?: FormReference | null
}): DocumentReference | null {
  if (value.document_reference) return value.document_reference
  const form = value.form_reference
  return form ? { document_id: form.form_id, name: form.name, role: 'form' } : null
}

function ConversationTurn({ turn, assistantContent, processing = false }: {
  turn: ChatTurn; assistantContent?: ReactNode; processing?: boolean
}) {
  const result = turn.result
  const evidence = result?.evidence ?? []
  const answerTitleId = `answer-title-${turn.id}`
  const evidenceTitleId = `evidence-title-${turn.id}`

  return (
    <article className="chat-turn">
      <div className="user-message">
        <span>Tu</span>
        <p>{turn.question}</p>
        {turn.document_reference && <small className="chat-form-reference">@{turn.document_reference.name}</small>}
      </div>

      <AssistantMessage id={answerTitleId} model={result?.model}
        busy={(!result && !turn.error) || processing} error={turn.error}>
          {assistantContent ?? (result?.answer && <p>{result.answer}</p>)}
          {!result?.answer && result?.notice && <p>{result.notice}</p>}
          {result && result.missing_information.length > 0 && (
            <div className="missing-information">
              <strong>Informazioni mancanti</strong>
              <ul>
                {result.missing_information.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          )}
      </AssistantMessage>

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
                  <span className="evidence-fragment">{item.role === 'form' ? 'Modulo' : 'Fonte'}</span>
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
  const [changingModel, setChangingModel] = useState(false)
  const [conversationLoading, setConversationLoading] = useState(false)
  const [conversationError, setConversationError] = useState<string | null>(null)
  const [documentReference, setDocumentReference] = useState<DocumentReference | null>(null)
  const [mention, setMention] = useState<{ start: number; end: number; query: string } | null>(null)
  const [mentionIndex, setMentionIndex] = useState(0)
  const documents = (project?.files.filter((file) => ['form', 'source'].includes(file.kind)) ?? [])
    .sort((a, b) => Number(b.kind === 'form') - Number(a.kind === 'form'))
  const selectedDocument = documents.find((file) => file.id === documentReference?.document_id)
  const mentionOptions = documents.filter((file) => file.name.toLocaleLowerCase().includes(mention?.query.toLocaleLowerCase() ?? ''))
  const answerRequest = useRef<AbortController | null>(null)
  const compilation = useCompilationSession(projectId, conversationId, undefined,
    searching || conversationLoading || changingModel, answerRequest)
  // A freshly created chat must finish navigation before it can accept another mutation.
  const activeSession = compilation.session?.conversation_id === conversationId ? compilation.session : null
  const sessionStateUnavailable = Boolean(conversationId && compilation.error && !compilation.session)
  const composerRef = useDismissibleMenu<HTMLFormElement>(Boolean(mention), () => setMention(null))
  const turnSequence = useRef(0)
  const chatThread = useRef<HTMLDivElement>(null)
  const stickToBottom = useRef(true)
  const composerInput = useRef<HTMLTextAreaElement>(null)
  const activeConversation = useRef<string | null>(conversationId ?? null)
  const loadedConversation = useRef<string | null>(null)
  const projectMenuRef = useDismissibleMenu<HTMLDivElement>(
    menuOpen,
    () => setMenuOpen(false),
  )

  useEffect(() => {
    setSearching(false)
    return () => {
      answerRequest.current?.abort()
      answerRequest.current = null
    }
  }, [projectId, conversationId])

  useEffect(() => {
    setPrompt('')
    setTurns([])
    setSearching(false)
    setConversationError(null)
    setDocumentReference(null)
    setMention(null)
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
      setDocumentReference(null)
      setMention(null)
      return
    }
    if (loadedConversation.current === conversationId) return

    const controller = new AbortController()
    activeConversation.current = conversationId
    setTurns([])
    setPrompt('')
    setDocumentReference(null)
    setMention(null)
    setConversationLoading(true)
    setConversationError(null)
    api.conversation(projectId, conversationId, controller.signal)
      .then((conversation) => {
        if (controller.signal.aborted) return
        activeConversation.current = conversation.id
        loadedConversation.current = conversation.id
        setDocumentReference(documentReferenceOf(conversation))
        setTurns(conversation.turns.map((turn) => ({
          id: `turn-${turn.id}`,
          question: turn.question,
          document_reference: documentReferenceOf(turn),
          result: {
            ...turn,
            conversation_id: conversation.id,
            turn_id: turn.id,
          },
          error: null,
        })))
      })
      .catch((reason) => {
        if (controller.signal.aborted) return
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
    if (!thread || !stickToBottom.current) return
    const frame = requestAnimationFrame(() => {
      thread.scrollTo({ top: thread.scrollHeight,
        behavior: window.matchMedia?.('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' })
    })
    return () => cancelAnimationFrame(frame)
  }, [turns, activeSession?.chat?.question?.message, activeSession?.status,
      activeSession?.last_generation?.id])

  useLayoutEffect(() => {
    const input = composerInput.current
    if (!input) return
    input.style.height = 'auto'
    input.style.height = `${input.scrollHeight}px`
  }, [prompt, turns.length])

  if (loading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (error || !project) {
    return <AppShell active="projects"><ErrorState message={error ?? 'Progetto non trovato'} /></AppShell>
  }
  const activeProjectId = project.id
  const activeProjectTitle = project.title

  async function submitPrompt(event: FormEvent) {
    event.preventDefault()
    const query = prompt.trim()
    if (!query || answerRequest.current || searching || conversationLoading || changingModel
      || compilation.loading || sessionStateUnavailable || compilation.isProcessing()) return
    const controller = new AbortController()
    answerRequest.current = controller
    const turnId = `local-${++turnSequence.current}`
    stickToBottom.current = true
    setTurns((current) => [
      ...current.map((turn, index) => {
        if (index !== current.length - 1 || !turn.result || !activeSession) return turn
        const answer = compilationReplyParagraphs(activeSession, turn.result, false, compilation.error).join('\n\n')
        return answer ? { ...turn, result: { ...turn.result, answer } } : turn
      }),
      { id: turnId, question: query, result: null, error: null,
        document_reference: selectedDocument ? documentReference : null },
    ])
    setPrompt('')
    setMention(null)
    setSearching(true)
    try {
      const result = await api.projectAnswer(
        activeProjectId,
        query,
        activeConversation.current,
        controller.signal,
        selectedDocument?.id,
        activeSession ? { session_id: activeSession.id, version: activeSession.version } : undefined,
      )
      if (controller.signal.aborted) return
      activeConversation.current = result.conversation_id
      loadedConversation.current = result.conversation_id
      setTurns((current) => current.map((turn) => (
        turn.id === turnId
          ? { ...turn, id: `turn-${result.turn_id}`, result }
          : turn
      )))
      if (result.compilation) compilation.refresh()
      if (conversationId !== result.conversation_id) {
        navigate(
          `/projects/${activeProjectId}/conversations/${result.conversation_id}`,
          { replace: true },
        )
      }
    } catch (reason) {
      if (controller.signal.aborted) return
      if (activeSession) compilation.refresh()
      const message = reason instanceof Error ? reason.message : 'Ricerca non riuscita'
      setTurns((current) => current.map((turn) => (
        turn.id === turnId ? { ...turn, error: message } : turn
      )))
    } finally {
      if (answerRequest.current === controller) {
        answerRequest.current = null
        setSearching(false)
      }
    }
  }

  function handleComposerKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.nativeEvent.isComposing) return
    if (mention) {
      if (event.key === 'Escape') { event.preventDefault(); setMention(null); return }
      if (['ArrowDown', 'ArrowUp'].includes(event.key)) {
        event.preventDefault()
        setMentionIndex((index) => (index + (event.key === 'ArrowDown' ? 1 : -1) + Math.max(1, mentionOptions.length)) % Math.max(1, mentionOptions.length))
        return
      }
      if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault()
        const option = mentionOptions[mentionIndex] ?? mentionOptions[0]
        if (option) selectMention(option)
        return
      }
    }
    if (event.key !== 'Enter' || event.shiftKey || event.nativeEvent.isComposing) return
    event.preventDefault()
    event.currentTarget.form?.requestSubmit()
  }

  function selectMention(document: ProjectFile) {
    if (!mention || compilation.isProcessing() || compilation.loading || searching) return
    setDocumentReference({ document_id: document.id, name: document.name,
      role: document.kind === 'form' ? 'form' : 'source' })
    setPrompt(prompt.slice(0, mention.start) + prompt.slice(mention.end))
    setMention(null)
    composerInput.current?.focus()
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

  const latestTurn = turns.at(-1)
  const sessionProcessing = compilation.processing || compilation.loading
  const sessionMessage = activeSession ? (
    <CompilationReply key={activeSession.id} session={activeSession} response={latestTurn?.result}
      pending={Boolean(latestTurn && !latestTurn.result && !latestTurn.error)}
      processing={sessionProcessing} locked={sessionProcessing || searching || changingModel}
      error={compilation.error} onRetry={compilation.refresh} />
  ) : null

  const composer = (
    <form
      ref={composerRef}
      className={`composer${turns.length > 0 || activeSession ? ' composer--docked' : ''}`}
      onSubmit={submitPrompt}
    >
      {selectedDocument && <div className="composer-mention">
        <span className="composer-mention-chip"><FileText size={14} /><span>@{selectedDocument.name}</span>
          <button type="button" className="icon-button" aria-label="Rimuovi riferimento al documento" title="Rimuovi riferimento al documento"
            disabled={compilation.processing || compilation.loading || searching} onClick={() => setDocumentReference(null)}><X size={14} /></button>
        </span>
      </div>}
      <textarea
        ref={composerInput}
        aria-label="Messaggio per Mapi RAG"
        placeholder="Come posso aiutarti? Usa @ per scegliere un documento"
        maxLength={MAX_PROMPT_LENGTH}
        value={prompt}
        aria-controls={mention ? 'composer-document-options' : undefined}
        aria-activedescendant={mention && mentionOptions[mentionIndex] ? `document-option-${mentionOptions[mentionIndex].id}` : undefined}
        onChange={(event) => {
          const text = event.target.value
          const end = event.target.selectionStart
          const match = /(?:^|\s)@([^@\s]*)$/.exec(text.slice(0, end))
          setPrompt(text)
          setMentionIndex(0)
          setMention(match && !compilation.processing && !compilation.loading && !searching ? { start: end - match[1].length - 1, end, query: match[1] } : null)
        }}
        onKeyDown={handleComposerKeyDown}
      />
      {mention && <div className="composer-mention-menu" id="composer-document-options" role="listbox" aria-label="Documenti del progetto">
        {mentionOptions.length === 0 && <p>Nessun documento corrispondente nel progetto</p>}
        {(['form', 'source'] as const).map((role) => {
          const options = mentionOptions.filter((file) => file.kind === role)
          const label = role === 'form' ? 'Moduli da compilare' : 'Bandi e fonti'
          return options.length > 0 && <div role="group" aria-label={label} key={role}>
            <p className="composer-mention-heading" aria-hidden="true">{label}</p>
            {options.map((document) => <button type="button" role="option" id={`document-option-${document.id}`}
              aria-selected={mentionOptions[mentionIndex]?.id === document.id} key={document.id}
              onClick={() => selectMention(document)}>{document.name}</button>)}
          </div>
        })}
      </div>}
      {!compilation.session && compilation.error && <div>
        <p role="alert">{compilation.error}</p>
        <button type="button" className="button" disabled={compilation.busy} onClick={compilation.refresh}>Riprova caricamento sessione</button>
      </div>}
      {compilation.busy && !activeSession && <p role="status">Preparazione della compilazione…</p>}
      <div className="composer-tools">
        <button
          className={`composer-mention-trigger${mention ? ' is-active' : ''}`}
          type="button"
          aria-label="Aggiungi un documento"
          title="Aggiungi un documento"
          disabled={searching || conversationLoading || changingModel || compilation.loading
            || compilation.processing || documents.length === 0}
          onClick={() => {
            const position = composerInput.current?.selectionStart ?? prompt.length
            setMention({ start: position, end: position, query: '' })
            setMentionIndex(0)
            composerInput.current?.focus()
          }}
        >
          <Plus size={19} />
        </button>
        <ProjectModelSelector key={project.id} projectId={project.id}
          disabled={searching || conversationLoading || compilation.processing || compilation.loading} onChanging={setChangingModel} />
        <button
          className="send-button"
          type="submit"
          aria-label="Invia"
          disabled={!prompt.trim() || searching || conversationLoading || changingModel || compilation.processing || compilation.loading || sessionStateUnavailable}
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
        <section className={`workspace-main${turns.length > 0 || activeSession ? ' workspace-main--conversation' : ''}`}>
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
          ) : turns.length === 0 && !activeSession ? (
            <>
              {composer}

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
              <div className="chat-thread" ref={chatThread}
                onScroll={(event) => {
                  const element = event.currentTarget
                  stickToBottom.current =
                    element.scrollHeight - element.scrollTop - element.clientHeight < 140
                }}>
                {turns.map((turn, index) => (
                  <div key={turn.id}>
                    <ConversationTurn
                      turn={turn}
                      assistantContent={index === turns.length - 1 ? sessionMessage ?? undefined : undefined}
                      processing={index === turns.length - 1 && Boolean(activeSession) && sessionProcessing}
                    />
                  </div>
                ))}
                {!turns.length && sessionMessage && <AssistantMessage id="recovered-answer" busy={sessionProcessing}>
                  {sessionMessage}
                </AssistantMessage>}
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
