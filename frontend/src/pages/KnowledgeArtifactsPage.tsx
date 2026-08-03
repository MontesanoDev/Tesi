import { FileText, Globe2, Save } from 'lucide-react'
import { useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import { useProject } from '../hooks/useProject'
import type {
  KnowledgeArtifactDetail,
  KnowledgeArtifactSummary,
  StatusTone,
} from '../types'

function artifactTone(artifact: KnowledgeArtifactSummary): StatusTone {
  if (artifact.scope === 'global') return 'info'
  if (artifact.status === 'Bozza aggiornata' || artifact.status === 'Bozza') return 'warning'
  if (artifact.status === 'Verificato') return 'success'
  return 'purple'
}

export function KnowledgeArtifactsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const { project, loading: projectLoading, error: projectError } = useProject(projectId)
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [artifact, setArtifact] = useState<KnowledgeArtifactDetail | null>(null)
  const [content, setContent] = useState('')
  const [listLoading, setListLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)
  const [savedMessage, setSavedMessage] = useState<string | null>(null)

  useEffect(() => {
    if (!projectId) return
    const controller = new AbortController()
    setListLoading(true)
    setError(null)
    api.projectArtifacts(projectId, controller.signal)
      .then((items) => {
        setArtifacts(items)
        setSelectedId((current) => {
          if (current && items.some((item) => item.id === current)) return current
          return items.find((item) => item.kind === 'call_facts')?.id ?? items[0]?.id ?? null
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
  }, [projectId])

  useEffect(() => {
    if (!projectId || !selectedId) return
    const controller = new AbortController()
    setDetailLoading(true)
    setError(null)
    setSavedMessage(null)
    api.projectArtifact(projectId, selectedId, controller.signal)
      .then((item) => {
        setArtifact(item)
        setContent(item.content)
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
      setSavedMessage(`Versione ${updated.version} salvata e indicizzata.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      setSaving(false)
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

  return (
    <AppShell active="projects" project={project}>
      <button
        className="back-link"
        type="button"
        onClick={() => navigate(`/projects/${project.id}/settings`)}
      >
        ← Impostazioni progetto
      </button>
      <div className="knowledge-workspace">
        <header className="page-heading knowledge-heading">
          <div>
            <h1>Conoscenza Markdown</h1>
            <p>Artefatti leggibili, revisionabili e indicizzati nel progetto</p>
          </div>
          <span>{artifacts.length} artefatti collegati</span>
        </header>

        {error && <div className="knowledge-error" role="alert">{error}</div>}

        <div className="artifact-layout">
          <nav className="artifact-list" aria-label="Artefatti Markdown">
            <span className="section-label">File di conoscenza</span>
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
                  {item.scope === 'global' ? <Globe2 size={17} /> : <FileText size={17} />}
                  <span>
                    <strong>{item.title}</strong>
                    <small>{item.filename} · v{item.version}</small>
                  </span>
                  <StatusPill tone={artifactTone(item)}>
                    {item.scope === 'global' ? 'Globale' : 'Progetto'}
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
                  <span>{artifact.chunk_count} frammenti indicizzati</span>
                  <span>{artifact.scope === 'global' ? 'Scope globale' : 'Scope progetto'}</span>
                </div>
                <textarea
                  className="markdown-editor"
                  aria-label={`Contenuto di ${artifact.title}`}
                  value={content}
                  readOnly={!artifact.editable}
                  spellCheck={false}
                  onChange={(event) => setContent(event.target.value)}
                />
                <footer className="artifact-editor-footer">
                  <div>
                    {artifact.editable ? (
                      <span>{content.split('\n').length} righe · {dirty ? 'Modifiche non salvate' : 'Salvato'}</span>
                    ) : (
                      <span>Gli artefatti globali sono in sola lettura in questo progetto.</span>
                    )}
                    {savedMessage && <strong>{savedMessage}</strong>}
                  </div>
                  <button
                    className="button button--primary artifact-save"
                    type="button"
                    disabled={!dirty || saving || !artifact.editable}
                    onClick={saveArtifact}
                  >
                    <Save size={16} /> {saving ? 'Salvataggio' : 'Salva e indicizza'}
                  </button>
                </footer>
              </>
            )}
          </section>
        </div>
      </div>
    </AppShell>
  )
}
