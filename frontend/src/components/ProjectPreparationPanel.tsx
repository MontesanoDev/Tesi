import {
  ChevronRight,
  LayoutTemplate,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { DocumentCompilationSummary, KnowledgeArtifactSummary, ProjectDetail, StatusTone } from '../types'
import { StatusPill } from './StatusPill'

function workflowTone(status: string): StatusTone {
  if (status === 'Disponibile' || status === 'Da completare') return 'info'
  if (status === 'Verificato') return 'success'
  if (status === 'Da estrarre' || status === 'Da generare') return 'info'
  if (status === 'Bozza' || status === 'Bozza aggiornata' || status === 'Da verificare') {
    return 'warning'
  }
  return 'purple'
}

export function ProjectPreparationPanel({ project }: { project: ProjectDetail }) {
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])
  const [compilations, setCompilations] = useState<DocumentCompilationSummary[]>([])

  useEffect(() => {
    const controller = new AbortController()
    setArtifacts([])
    api.projectArtifacts(project.id, controller.signal)
      .then(setArtifacts)
      .catch((reason) => {
        if (reason instanceof DOMException && reason.name === 'AbortError') return
        setArtifacts([])
      })
    return () => controller.abort()
  }, [project.id])

  useEffect(() => {
    const controller = new AbortController()
    setCompilations([])
    api.documentCompilations(project.id, controller.signal)
      .then((items) => { if (!controller.signal.aborted) setCompilations(items) })
      .catch(() => { if (!controller.signal.aborted) setCompilations([]) })
    return () => controller.abort()
  }, [project.id])

  function templateStatus() {
    if (compilations.length) return 'Da verificare'
    const compilation = artifacts.find((item) => item.kind === 'output_draft')
    if (compilation && compilation.status !== 'Da generare') {
      return compilation.status
    }
    const artifact = artifacts.find((item) => item.kind === 'template')
    if (artifact) return artifact.status
    return 'Bozza'
  }

  function templateDetail() {
    if (compilations.length) return compilations.length === 1
      ? '1 compilazione Word' : `${compilations.length} compilazioni Word`
    const compilation = artifacts.find((item) => item.kind === 'output_draft')
    if (compilation && compilation.status !== 'Da generare') {
      return `Compilazione v${compilation.version}`
    }
    const artifact = artifacts.find((item) => item.kind === 'template')
    return artifact ? `Versione ${artifact.version}` : 'Versione 1'
  }

  const status = templateStatus()
  return (
    <section
      className="knowledge-section project-preparation"
      aria-labelledby="project-preparation-title"
    >
      <div className="project-preparation-heading">
        <h2 id="project-preparation-title">Preparazione candidatura</h2>
      </div>
      <div className="project-workflow-list">
        <Link className="project-workflow-row" to={`/projects/${project.id}/knowledge?artifact=template`}>
          <LayoutTemplate size={17} />
          <span><strong>Template</strong><small>{templateDetail()}</small></span>
          <StatusPill tone={workflowTone(status)}>{status}</StatusPill>
          <ChevronRight size={16} />
        </Link>
      </div>
    </section>
  )
}
