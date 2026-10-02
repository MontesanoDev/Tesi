import { X } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { KnowledgeArtifactDetail, KnowledgeArtifactSummary } from '../types'
import { LoadingState } from './LoadingState'
import { TemplateWorkspace } from './TemplateWorkspace'
import './ProjectDocumentsPanel.css'

interface Props {
  projectId: string
  open: boolean
  initialFormat: 'docx' | 'text'
  onClose: () => void
}

export function ProjectDocumentsPanel({ open, ...props }: Props) {
  const [visited, setVisited] = useState(open)
  const heading = useRef<HTMLHeadingElement>(null)
  useEffect(() => {
    if (open) {
      setVisited(true)
      heading.current?.focus({ preventScroll: true })
      heading.current?.scrollIntoView({ block: 'nearest' })
    }
  }, [open])

  // Collapse without unmounting: selected files and pending work stay intact.
  if (!visited && !open) return null
  return <section id="project-documents" className="project-documents" hidden={!open} aria-labelledby="project-documents-title">
    <header className="project-documents-heading">
      <h2 id="project-documents-title" ref={heading} tabIndex={-1}>Moduli e bozze</h2>
      <button className="icon-button" type="button" aria-label="Chiudi moduli e bozze" onClick={props.onClose}>
        <X size={18} />
      </button>
    </header>
    <DocumentsContent {...props} />
  </section>
}

function DocumentsContent({ projectId, initialFormat }: Omit<Props, 'open'>) {
  const [artifacts, setArtifacts] = useState<KnowledgeArtifactSummary[]>([])
  const [template, setTemplate] = useState<KnowledgeArtifactDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [dirty, setDirty] = useState(false)
  const onUpdated = useCallback((updated: KnowledgeArtifactDetail) => {
    setArtifacts((current) => current.map((item) => item.id === updated.id ? updated : item))
    setTemplate((current) => current?.id === updated.id ? updated : current)
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setTemplate(null)
    setArtifacts([])
    setError(null)
    api.projectArtifacts(projectId, controller.signal)
      .then(async (items) => {
        if (controller.signal.aborted) return
        const model = items.find((item) => item.kind === 'template')
        if (!model) throw new Error('Modelli non disponibili per questo progetto')
        const detail = await api.projectArtifact(projectId, model.id, controller.signal)
        if (controller.signal.aborted) return
        setArtifacts(items)
        setTemplate(detail)
      })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Documenti non disponibili')
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [projectId])

  const output = artifacts.find((item) => item.kind === 'output_draft')
  return <div className="project-documents-content">
    {error && <div className="knowledge-error" role="alert">{error}</div>}
    {loading ? <LoadingState label="Caricamento moduli" /> : template && <TemplateWorkspace
      projectId={projectId} template={template} outputId={output?.id}
      initialFormat={initialFormat}
      initialView={output && output.status !== 'Da generare' ? 'compilation' : 'model'}
      embedded onUpdated={onUpdated} onDirtyChange={setDirty} />}
    {dirty && <p className="project-documents-pending">Ci sono modifiche non salvate o una compilazione in preparazione.</p>}
  </div>
}
