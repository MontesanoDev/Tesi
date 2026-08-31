import {
  ChevronRight,
  ClipboardList,
  FileOutput,
  LayoutTemplate,
  ListChecks,
} from 'lucide-react'
import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import type { KnowledgeArtifactSummary, ProjectDetail, StatusTone } from '../types'
import { StatusPill } from './StatusPill'

const WORKFLOW_ITEMS = [
  { kind: 'call_facts', label: 'Call Facts' },
  { kind: 'project_facts', label: 'Dati del progetto' },
  { kind: 'template', label: 'Template' },
  { kind: 'output_draft', label: 'Draft' },
] as const

function workflowTone(status: string): StatusTone {
  if (status === 'Verificato') return 'success'
  if (status === 'Da estrarre' || status === 'Da generare') return 'info'
  if (status === 'Bozza' || status === 'Bozza aggiornata' || status === 'Da verificare') {
    return 'warning'
  }
  return 'purple'
}

function WorkflowIcon({ kind }: { kind: (typeof WORKFLOW_ITEMS)[number]['kind'] }) {
  if (kind === 'call_facts') return <ListChecks size={17} />
  if (kind === 'project_facts') return <ClipboardList size={17} />
  if (kind === 'template') return <LayoutTemplate size={17} />
  return <FileOutput size={17} />
}

export function ProjectPreparationPanel({ project }: { project: ProjectDetail }) {
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])

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

  function statusFor(kind: (typeof WORKFLOW_ITEMS)[number]['kind']) {
    const artifact = artifacts.find((item) => item.kind === kind)
    if (artifact) return artifact.status
    if (kind === 'call_facts') {
      if (project.call_fact_count === 0) return 'Da estrarre'
      return project.missing_fact_count > 0 ? 'Da verificare' : 'Verificato'
    }
    if (kind === 'output_draft') return 'Da generare'
    return 'Bozza'
  }

  function detailFor(kind: (typeof WORKFLOW_ITEMS)[number]['kind']) {
    if (kind === 'call_facts') {
      const factLabel = project.call_fact_count === 1
        ? '1 fatto'
        : `${project.call_fact_count} fatti`
      return `${factLabel} · ${project.missing_fact_count} mancanti`
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
