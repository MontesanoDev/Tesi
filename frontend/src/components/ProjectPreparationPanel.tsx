import {
  ChevronRight,
  ClipboardList,
  LayoutTemplate,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { DocumentCompilationSummary, KnowledgeArtifactSummary, ProjectDetail, StatusTone } from '../types'
import { StatusPill } from './StatusPill'

const WORKFLOW_ITEMS = [
  { kind: 'project_facts', label: 'Dati del progetto' },
  { kind: 'template', label: 'Template' },
] as const

function workflowTone(status: string): StatusTone {
  if (status === 'Disponibile' || status === 'Da completare') return 'info'
  if (status === 'Verificato') return 'success'
  if (status === 'Da estrarre' || status === 'Da generare') return 'info'
  if (status === 'Bozza' || status === 'Bozza aggiornata' || status === 'Da verificare') {
    return 'warning'
  }
  return 'purple'
}

function WorkflowIcon({ kind }: { kind: (typeof WORKFLOW_ITEMS)[number]['kind'] }) {
  if (kind === 'project_facts') return <ClipboardList size={17} />
  return <LayoutTemplate size={17} />
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

  function statusFor(kind: (typeof WORKFLOW_ITEMS)[number]['kind']) {
    if (kind === 'project_facts') return project.call_fact_count > 0 ? 'Disponibile' : 'Da completare'
    if (kind === 'template' && compilations.length) return 'Da verificare'
    const compilation = artifacts.find((item) => item.kind === 'output_draft')
    if (kind === 'template' && compilation && compilation.status !== 'Da generare') {
      return compilation.status
    }
    const artifact = artifacts.find((item) => item.kind === kind)
    if (artifact) return artifact.status
    return 'Bozza'
  }

  function detailFor(kind: (typeof WORKFLOW_ITEMS)[number]['kind']) {
    if (kind === 'template' && compilations.length) return compilations.length === 1
      ? '1 compilazione Word' : `${compilations.length} compilazioni Word`
    const compilation = artifacts.find((item) => item.kind === 'output_draft')
    if (kind === 'template' && compilation && compilation.status !== 'Da generare') {
      return `Compilazione v${compilation.version}`
    }
    if (kind === 'project_facts') {
      const factLabel = project.call_fact_count === 1
        ? '1 dato estratto'
        : `${project.call_fact_count} dati estratti`
      return factLabel
    }
    const artifact = artifacts.find((item) => item.kind === kind)
    return artifact ? `Versione ${artifact.version}` : 'Versione 1'
  }

  return (
    <section
      className="knowledge-section project-preparation"
      aria-labelledby="project-preparation-title"
    >
      <div className="project-preparation-heading">
        <h2 id="project-preparation-title">Preparazione candidatura</h2>
      </div>
      <div className="project-workflow-list">
        {WORKFLOW_ITEMS.map((item) => {
          const status = statusFor(item.kind)
          return (
            <Link
              className="project-workflow-row"
              key={item.kind}
              to={`/projects/${project.id}/knowledge?artifact=${item.kind}`}
            >
              <WorkflowIcon kind={item.kind} />
              <span>
                <strong>{item.label}</strong>
                <small>{detailFor(item.kind)}</small>
              </span>
              <StatusPill tone={workflowTone(status)}>{status}</StatusPill>
              <ChevronRight size={16} />
            </Link>
          )
        })}
      </div>
    </section>
  )
}
