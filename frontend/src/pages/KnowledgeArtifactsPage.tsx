import { FileOutput, FileText, LayoutTemplate, Save, WandSparkles } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { CallFactsReviewPanel } from '../components/CallFactsReviewPanel'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import { useProject } from '../hooks/useProject'
import type {
  CallFactsReview,
  KnowledgeArtifactDetail,
  KnowledgeArtifactSummary,
  StatusTone,
} from '../types'

function artifactTone(artifact: KnowledgeArtifactSummary): StatusTone {
  if (artifact.scope === 'global') return 'info'
  if (
    artifact.status === 'Bozza aggiornata'
    || artifact.status === 'Bozza'
    || artifact.status === 'Da verificare'
  ) return 'warning'
  if (artifact.status === 'Verificato') return 'success'
  return 'purple'
}

export function KnowledgeArtifactsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const requestedArtifactKind = searchParams.get('artifact')
  const { project, loading: projectLoading, error: projectError } = useProject(projectId)
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [artifact, setArtifact] = useState<KnowledgeArtifactDetail | null>(null)
  const [content, setContent] = useState('')
  const [listLoading, setListLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const [generatingDraft, setGeneratingDraft] = useState(false)
  const [savedMessage, setSavedMessage] = useState<string | null>(null)
  const [viewMode, setViewMode] = useState<'review' | 'markdown'>('markdown')
  const [review, setReview] = useState<CallFactsReview | null>(null)
  const [reviewLoading, setReviewLoading] = useState(false)
  const [reviewRefresh, setReviewRefresh] = useState(0)
  const pendingSelectionMessage = useRef<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    const controller = new AbortController()
    setListLoading(true)
    setError(null)
    api.projectArtifacts(projectId, controller.signal)
      .then((items) => {
        setArtifacts(items)
        setSelectedId((current) => {
          const requested = items.find((item) => item.kind === requestedArtifactKind)
          if (requested) return requested.id
          if (current && items.some((item) => item.id === current)) return current
          return items.find((item) => item.kind === 'call_facts')?.id
            ?? items[0]?.id
            ?? null
        })
      })
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setError(reason instanceof Error ? reason.message : 'Artefatti non disponibili')
      })
      .finally(() => {
        if (!controller.signal.aborted) setListLoading(false)
      })
    return () => controller.abort()
  }, [projectId, requestedArtifactKind])

  useEffect(() => {
    if (!projectId || !selectedId) return
    const controller = new AbortController()
    setDetailLoading(true)
    setArtifact(null)
    setError(null)
    setSavedMessage(pendingSelectionMessage.current)
    pendingSelectionMessage.current = null
    api.projectArtifact(projectId, selectedId, controller.signal)
      .then((item) => {
        setArtifact(item)
        setContent(item.content)
        setViewMode(item.kind === 'call_facts' ? 'review' : 'markdown')
      })
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setError(reason instanceof Error ? reason.message : 'Artefatto non disponibile')
      })
      .finally(() => {
        if (!controller.signal.aborted) setDetailLoading(false)
      })
    return () => controller.abort()
  }, [projectId, selectedId])

  useEffect(() => {
    if (!projectId || artifact?.kind !== 'call_facts') {
      setReview(null)
      setReviewLoading(false)
      return
    }
    const controller = new AbortController()
    setReviewLoading(true)
    api.callFactsReview(projectId, controller.signal)
      .then(setReview)
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setError(reason instanceof Error ? reason.message : 'Revisione non disponibile')
      })
      .finally(() => {
        if (!controller.signal.aborted) setReviewLoading(false)
      })
    return () => controller.abort()
  }, [projectId, artifact?.id, artifact?.kind, reviewRefresh])

  async function saveArtifact() {
    if (!projectId || !artifact || !artifact.editable || content === artifact.content) return
    setSaving(true)
    setError(null)
    setSavedMessage(null)
    try {
      const updated = await api.updateProjectArtifact(projectId, artifact.id, content)
      setArtifact(updated)
      setContent(updated.content)
      setArtifacts((current) => current.map((item) => (
        item.id === updated.id ? updated : item
      )))
      if (updated.kind === 'call_facts') setReviewRefresh((current) => current + 1)
      setSavedMessage(
        updated.kind === 'output_draft'
          ? `Versione ${updated.version} salvata per la revisione.`
          : `Versione ${updated.version} salvata e indicizzata.`,
      )
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      setSaving(false)
    }
  }

  async function extractFacts() {
    if (!projectId || !artifact || artifact.kind !== 'call_facts' || dirty) return
    setExtracting(true)
    setError(null)
    setSavedMessage(null)
    try {
      const result = await api.extractCallFacts(projectId)
      setArtifact(result.artifact)
      setContent(result.artifact.content)
      setArtifacts((current) => current.map((item) => (
        item.id === result.artifact.id ? result.artifact : item
      )))
      setReviewRefresh((current) => current + 1)
      setSavedMessage(
        `${result.fact_count} fatti estratti da ${result.evidence_count} frammenti · `
        + `${result.missing_count} informazioni mancanti.`,
      )
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Estrazione non riuscita')
    } finally {
      setExtracting(false)
    }
  }

  async function generateDraft() {
    if (
      !projectId
      || !artifact
      || !['template', 'output_draft'].includes(artifact.kind)
      || dirty
    ) return
    setGeneratingDraft(true)
    setError(null)
    setSavedMessage(null)
    try {
      const result = await api.generateDraft(projectId)
      const message = (
        `Draft generato da ${result.used_fact_count} di ${result.verified_fact_count} `
        + `Call Facts verificati · ${result.missing_information.length} TODO.`
      )
      setArtifacts((current) => current.map((item) => (
        item.id === result.artifact.id ? result.artifact : item
      )))
      if (artifact.id === result.artifact.id) {
        setArtifact(result.artifact)
        setContent(result.artifact.content)
        setSavedMessage(message)
      } else {
        pendingSelectionMessage.current = message
        setSelectedId(result.artifact.id)
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Generazione del draft non riuscita')
    } finally {
      setGeneratingDraft(false)
    }
  }

  if (projectLoading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (projectError || !project) {
    return (
      <AppShell active="projects">
        <ErrorState message={projectError ?? 'Progetto non trovato'} />
      </AppShell>
    )
  }

  const dirty = Boolean(artifact && content !== artifact.content)
  const canExtract = Boolean(artifact?.editable && artifact.kind === 'call_facts')
  const canGenerateDraft = Boolean(
    artifact?.editable && ['template', 'output_draft'].includes(artifact.kind),
  )

  function handleReviewUpdated(updated: CallFactsReview, message: string) {
    setReview(updated)
    setArtifact(updated.artifact)
    setContent(updated.artifact.content)
    setArtifacts((current) => current.map((item) => (
      item.id === updated.artifact.id ? updated.artifact : item
    )))
    setSavedMessage(message)
    setError(null)
  }

  return (
    <AppShell active="projects" project={project}>
      <button
        className="back-link"
        type="button"
        onClick={() => navigate(`/projects/${project.id}`)}
      >
        ← {project.title}
      </button>
      <div className="knowledge-workspace">
        <header className="page-heading knowledge-heading">
          <div>
            <h1>Preparazione candidatura</h1>
            <p>Dati verificati, struttura e bozza del progetto</p>
          </div>
          <span>{artifacts.length} artefatti collegati</span>
        </header>

        {error && <div className="knowledge-error" role="alert">{error}</div>}

        <div className="artifact-layout">
          <nav className="artifact-list" aria-label="Preparazione candidatura">
            <span className="section-label">Flusso di lavoro</span>
            {listLoading ? (
              <LoadingState label="Caricamento artefatti" />
            ) : (
              artifacts.map((item) => (
                <button
                  className={`artifact-list-item${selectedId === item.id ? ' is-active' : ''}`}
                  type="button"
                  key={item.id}
                  onClick={() => setSelectedId(item.id)}
                >
                  {item.kind === 'output_draft' ? (
                    <FileOutput size={17} />
                  ) : item.kind === 'template' ? (
                    <LayoutTemplate size={17} />
                  ) : (
                    <FileText size={17} />
                  )}
                  <span>
                    <strong>{item.title}</strong>
                    <small>{item.filename} · v{item.version}</small>
                  </span>
                  <StatusPill tone={artifactTone(item)}>
                    {item.status}
                  </StatusPill>
                </button>
              ))
            )}
          </nav>

          <section className="artifact-editor" aria-label="Editor Markdown">
            {detailLoading || !artifact ? (
              <LoadingState label="Caricamento Markdown" />
            ) : (
              <>
                <header className="artifact-editor-heading">
                  <div>
                    <span className="section-label">{artifact.filename}</span>
                    <h2>{artifact.title}</h2>
                  </div>
                  <StatusPill tone={artifactTone(artifact)}>{artifact.status}</StatusPill>
                </header>
                <div className="artifact-metadata">
                  <span>Versione {artifact.version}</span>
                  <span>
                    {artifact.kind === 'output_draft'
                      ? 'Output escluso dal RAG'
                      : `${artifact.chunk_count} frammenti indicizzati`}
                  </span>
                  <span>{artifact.scope === 'global' ? 'Scope globale' : 'Scope progetto'}</span>
                </div>
                {artifact.kind === 'call_facts' && (
                  <div className="artifact-view-tabs" role="tablist" aria-label="Vista Call Facts">
                    <button
                      className={viewMode === 'review' ? 'is-active' : ''}
                      type="button"
                      role="tab"
                      aria-selected={viewMode === 'review'}
                      onClick={() => setViewMode('review')}
                    >
                      Revisione
                    </button>
                    <button
                      className={viewMode === 'markdown' ? 'is-active' : ''}
                      type="button"
                      role="tab"
                      aria-selected={viewMode === 'markdown'}
                      onClick={() => setViewMode('markdown')}
                    >
                      Markdown
                    </button>
                  </div>
                )}
                {artifact.kind === 'call_facts' && viewMode === 'review' ? (
                  <CallFactsReviewPanel
                    projectId={project.id}
                    review={review}
                    loading={reviewLoading}
                    onUpdated={handleReviewUpdated}
                    onError={setError}
                  />
                ) : (
                  <textarea
                    className="markdown-editor"
                    aria-label={`Contenuto di ${artifact.title}`}
                    value={content}
                    readOnly={!artifact.editable}
                    spellCheck={false}
                    onChange={(event) => setContent(event.target.value)}
                  />
                )}
                <footer className="artifact-editor-footer">
                  <div>
                    {artifact.kind === 'call_facts' && viewMode === 'review' ? (
                      <span>Ogni revisione aggiorna e reindicizza automaticamente il Markdown.</span>
                    ) : artifact.editable ? (
                      <span>{content.split('\n').length} righe · {dirty ? 'Modifiche non salvate' : 'Salvato'}</span>
                    ) : (
                      <span>Gli artefatti globali sono in sola lettura in questo progetto.</span>
                    )}
                    {savedMessage && <strong>{savedMessage}</strong>}
                  </div>
                  <div className="artifact-actions">
                    {canExtract && (
                      <button
                        className="button artifact-extract"
                        type="button"
                        disabled={dirty || saving || extracting}
                        title={dirty ? 'Salva o annulla le modifiche prima di estrarre' : undefined}
                        onClick={extractFacts}
                      >
                        <WandSparkles size={16} />
                        {extracting
                          ? 'Estrazione in corso'
                          : artifact.status === 'Da estrarre'
                            ? 'Estrai dalle fonti'
                            : 'Riestrai dalle fonti'}
                      </button>
                    )}
                    {canGenerateDraft && (
                      <button
                        className="button artifact-generate"
                        type="button"
                        disabled={dirty || saving || extracting || generatingDraft}
                        title={dirty ? 'Salva o annulla le modifiche prima di generare' : undefined}
                        onClick={generateDraft}
                      >
                        <WandSparkles size={16} />
                        {generatingDraft
                          ? 'Generazione in corso'
                          : artifact.kind === 'output_draft' && artifact.status !== 'Da generare'
                            ? 'Rigenera draft'
                            : 'Genera draft'}
                      </button>
                    )}
                    {(artifact.kind !== 'call_facts' || viewMode === 'markdown') && (
                      <button
                        className="button button--primary artifact-save"
                        type="button"
                        disabled={
                          !dirty || saving || extracting || generatingDraft || !artifact.editable
                        }
                        onClick={saveArtifact}
                      >
                        <Save size={16} />{' '}
                        {saving
                          ? 'Salvataggio'
                          : artifact.kind === 'output_draft'
                            ? 'Salva revisione'
                            : 'Salva e indicizza'}
                      </button>
                    )}
                  </div>
                </footer>
              </>
            )}
          </section>
        </div>
      </div>
    </AppShell>
  )
}
