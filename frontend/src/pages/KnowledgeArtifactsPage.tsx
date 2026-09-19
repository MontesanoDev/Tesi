import { ClipboardList, LayoutTemplate } from 'lucide-react'
import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { ProjectFactsWorkspace } from '../components/ProjectFactsWorkspace'
import { TemplateWorkspace } from '../components/TemplateWorkspace'
import { useProject } from '../hooks/useProject'
import type { KnowledgeArtifactDetail, KnowledgeArtifactSummary } from '../types'

export function KnowledgeArtifactsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const requested = searchParams.get('artifact')
  const legacyOutputLink = requested === 'output_draft'
  const requestedKind = legacyOutputLink ? 'template' : requested === 'call_facts' ? 'project_facts' : requested
  const { project, loading: projectLoading, error: projectError } = useProject(projectId)
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [artifact, setArtifact] = useState<KnowledgeArtifactDetail | null>(null)
  const [listLoading, setListLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [dirty, setDirty] = useState(false)
  const onUpdated = useCallback((updated: KnowledgeArtifactDetail) => {
    setArtifacts((current) => current.map((item) => item.id === updated.id ? updated : item))
  }, [])

  useEffect(() => {
    if (!projectId) return
    const controller = new AbortController()
    setListLoading(true)
    setError(null)
    api.projectArtifacts(projectId, controller.signal)
      .then((items) => {
        if (controller.signal.aborted) return
        setArtifacts(items)
        setSelectedId(items.find((item) => item.kind === requestedKind)?.id
          ?? items.find((item) => item.kind === 'project_facts')?.id ?? null)
      })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Dati non disponibili')
      })
      .finally(() => { if (!controller.signal.aborted) setListLoading(false) })
    return () => controller.abort()
  }, [projectId, requestedKind])

  useEffect(() => {
    if (!projectId || !selectedId) return
    const controller = new AbortController()
    setDetailLoading(true)
    setArtifact(null)
    setError(null)
    api.projectArtifact(projectId, selectedId, controller.signal)
      .then((item) => { if (!controller.signal.aborted) setArtifact(item) })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Dati non disponibili')
      })
      .finally(() => { if (!controller.signal.aborted) setDetailLoading(false) })
    return () => controller.abort()
  }, [projectId, selectedId])

  if (projectLoading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (projectError || !project) return <AppShell active="projects">
    <ErrorState message={projectError ?? 'Progetto non trovato'} />
  </AppShell>

  const workflowArtifacts = artifacts.filter((item) => ['project_facts', 'template'].includes(item.kind))
  const output = artifacts.find((item) => item.kind === 'output_draft')
  function confirmLeave() {
    return !dirty || window.confirm('Operazione in corso o modifiche non salvate. Uscire comunque?')
  }

  return <AppShell active="projects" project={project}>
    <button className="back-link" type="button"
      onClick={() => { if (confirmLeave()) navigate(`/projects/${project.id}`) }}>← {project.title}</button>
    <div className="knowledge-workspace">
      <header className="page-heading knowledge-heading"><h1>Preparazione candidatura</h1></header>
      {error && <div className="knowledge-error" role="alert">{error}</div>}
      <div className="artifact-layout">
        <nav className="artifact-list" aria-label="Preparazione candidatura">
          <span className="section-label">Flusso di lavoro</span>
          {listLoading ? <LoadingState label="Caricamento dati" /> : workflowArtifacts.map((item) => (
            <button className={`artifact-list-item${selectedId === item.id ? ' is-active' : ''}`}
              type="button" key={item.id}
              onClick={() => { if (item.id !== selectedId && confirmLeave()) setSelectedId(item.id) }}>
              {item.kind === 'template' ? <LayoutTemplate size={17} /> : <ClipboardList size={17} />}
              <span><strong>{item.kind === 'template' ? 'Template' : 'Dati del progetto'}</strong>
                <small>{item.kind === 'template' ? 'Modello e compilazione' : 'Fonti e dati inseriti'}</small></span>
            </button>
          ))}
        </nav>
        <section className="artifact-editor" aria-label={artifact?.kind === 'template' ? 'Template' : 'Dati del progetto'}>
          {listLoading || detailLoading || !artifact ? <LoadingState label="Caricamento dati" />
            : artifact.kind === 'template' ? <TemplateWorkspace
              key={`${project.id}:${artifact.id}`} projectId={project.id} template={artifact}
              outputId={output?.id} initialView={legacyOutputLink || (output && output.status !== 'Da generare') ? 'compilation' : 'model'}
              initialFormat={legacyOutputLink ? 'text' : 'docx'} onUpdated={onUpdated} onDirtyChange={setDirty} />
              : <ProjectFactsWorkspace key={`${project.id}:${artifact.id}`} projectId={project.id}
                artifact={artifact} onUpdated={onUpdated} onDirtyChange={setDirty} />}
        </section>
      </div>
    </div>
  </AppShell>
}
