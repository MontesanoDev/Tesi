import { ChevronRight, Files } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import type { ProjectDetail } from '../types'

export function ProjectPreparationPanel({ project }: { project: ProjectDetail }) {
  const location = useLocation()
  const projectPath = `/projects/${project.id}`
  const pathname = location.pathname === projectPath || location.pathname.startsWith(`${projectPath}/conversations/`)
    ? location.pathname : projectPath
  const params = new URLSearchParams(location.search)
  const open = params.has('documents')
  if (!open) params.set('documents', 'docx')

  return <section className="knowledge-section project-preparation" aria-labelledby="project-preparation-title">
    <div className="project-preparation-heading">
      <h2 id="project-preparation-title">Preparazione candidatura</h2>
    </div>
    <div className="project-workflow-list">
      <Link className="project-workflow-row" to={`${pathname}?${params}`} replace
        aria-controls="project-documents" aria-expanded={open}>
        <Files size={17} />
        <span><strong>Moduli e bozze</strong><small>Compilazione e report</small></span>
        <ChevronRight size={16} />
      </Link>
    </div>
  </section>
}
