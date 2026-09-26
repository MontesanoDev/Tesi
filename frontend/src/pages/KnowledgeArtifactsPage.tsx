import { useCallback, useEffect, useState } from 'react'
import { useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { TemplateWorkspace } from '../components/TemplateWorkspace'
import { useProject } from '../hooks/useProject'
import type { KnowledgeArtifactDetail, KnowledgeArtifactSummary } from '../types'

export function KnowledgeArtifactsPage() {
  const { projectId } = useParams()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const requested = searchParams.get('artifact')
  const legacyOutputLink = requested === 'output_draft'
  const { project, loading: projectLoading, error: projectError } = useProject(projectId)
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])
  const [artifact, setArtifact] = useState<KnowledgeArtifactDetail | null>(null)
  const [listLoading, setListLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dirty, setDirty] = useState(false)
  const onUpdated = useCallback((updated: KnowledgeArtifactDetail) => {
    setArtifacts((current) => current.map((item) => item.id === updated.id ? updated : item))
    setArtifact((current) => current?.id === updated.id ? updated : current)
  }, [])

  useEffect(() => {
    if (!projectId) return
    const controller = new AbortController()
    setListLoading(true)
    setArtifacts([])
    setArtifact(null)
    setDirty(false)
    setError(null)
    api.projectArtifacts(projectId, controller.signal)
      .then(async (items) => {
        if (controller.signal.aborted) return
        const template = items.find((item) => item.kind === 'template')
        if (!template) throw new Error('Template non disponibile per questo progetto')
        const detail = await api.projectArtifact(projectId, template.id, controller.signal)
        if (controller.signal.aborted) return
        setArtifacts(items)
        setArtifact(detail)
      })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Dati non disponibili')
      })
      .finally(() => { if (!controller.signal.aborted) setListLoading(false) })
    return () => controller.abort()
  }, [projectId])

  if (projectLoading) return <AppShell active="projects"><LoadingState /></AppShell>
  if (projectError || !project) return <AppShell active="projects">
    <ErrorState message={projectError ?? 'Progetto non trovato'} />
  </AppShell>

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
        <section className="artifact-editor" aria-label="Template">
          {listLoading ? <LoadingState label="Caricamento template" />
            : artifact && <TemplateWorkspace
              key={`${project.id}:${artifact.id}`} projectId={project.id} template={artifact}
              outputId={output?.id} initialView={legacyOutputLink || (output && output.status !== 'Da generare') ? 'compilation' : 'model'}
              initialFormat={legacyOutputLink ? 'text' : 'docx'} onUpdated={onUpdated} onDirtyChange={setDirty} />}
        </section>
      </div>
    </div>
  </AppShell>
}
