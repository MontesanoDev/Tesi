import { Save, WandSparkles } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '../api'
import type { CallFactsReview, KnowledgeArtifactDetail } from '../types'
import { CallFactsReviewPanel } from './CallFactsReviewPanel'
import './ProjectFactsWorkspace.css'

interface Props {
  projectId: string
  artifact: KnowledgeArtifactDetail
  onUpdated: (artifact: KnowledgeArtifactDetail) => void
  onDirtyChange: (dirty: boolean) => void
}

export function ProjectFactsWorkspace({ projectId, artifact, onUpdated, onDirtyChange }: Props) {
  const [tab, setTab] = useState<'extracted' | 'entered'>('extracted')
  const [saved, setSaved] = useState(artifact)
  const [content, setContent] = useState(artifact.content)
  const [review, setReview] = useState<CallFactsReview | null>(null)
  const [loading, setLoading] = useState(true)
  const [operation, setOperation] = useState<'save' | 'extract' | null>(null)
  const [factDirty, setFactDirty] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [reload, setReload] = useState(0)
  const dirty = content !== saved.content
  const busy = Boolean(operation) || factDirty

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setReview(null)
    setError(null)
    api.callFactsReview(projectId, controller.signal)
      .then((result) => { if (!controller.signal.aborted) setReview(result) })
      .catch((reason) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Dati non disponibili')
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [projectId, reload])

  useEffect(() => {
    onDirtyChange(dirty || busy)
    return () => onDirtyChange(false)
  }, [dirty, busy, onDirtyChange])

  useEffect(() => {
    if (!dirty && !busy) return
    const beforeUnload = (event: BeforeUnloadEvent) => event.preventDefault()
    const beforeLink = (event: MouseEvent) => {
      const link = event.target instanceof Element ? event.target.closest('a') : null
      if (!link || link.target === '_blank' || link.hasAttribute('download')
        || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
      if (!window.confirm('Operazione in corso o dati non salvati. Uscire comunque?')) {
        event.preventDefault()
        event.stopPropagation()
      }
    }
    window.addEventListener('beforeunload', beforeUnload)
    document.addEventListener('click', beforeLink, true)
    return () => {
      window.removeEventListener('beforeunload', beforeUnload)
      document.removeEventListener('click', beforeLink, true)
    }
  }, [dirty, busy])

  async function save() {
    if (busy || !dirty || !content.trim() || !saved.editable) return
    setOperation('save')
    setError(null)
    setMessage(null)
    try {
      const updated = await api.updateProjectArtifact(projectId, saved.id, content)
      setSaved(updated)
      setContent(updated.content)
      onUpdated(updated)
      setMessage('Dati salvati.')
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      setOperation(null)
    }
  }

  async function extract() {
    if (busy || loading || !review || !saved.editable) return
    if (review.facts.length && !window.confirm(
      "Sostituire i dati estratti, incluse correzioni ed esclusioni? I dati inseriti per il progetto non cambiano.",
    )) return
    setOperation('extract')
    setError(null)
    setMessage(null)
    try {
      const result = await api.extractCallFacts(projectId)
      onUpdated(result.artifact)
      setReload((current) => current + 1)
      setMessage(result.fact_count === 1 ? '1 dato estratto.' : `${result.fact_count} dati estratti.`)
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Estrazione non riuscita')
    } finally {
      setOperation(null)
    }
  }

  return <div className="project-facts-workspace" aria-busy={Boolean(operation)}>
    <header className="artifact-editor-heading"><h2>Dati del progetto</h2></header>
    <div className="artifact-view-tabs" role="tablist" aria-label="Dati del progetto">
      {(['extracted', 'entered'] as const).map((item) => <button
        key={item} type="button" role="tab" id={`project-data-tab-${item}`}
        className={tab === item ? 'is-active' : ''} aria-selected={tab === item}
        aria-controls={`project-data-${item}`} tabIndex={tab === item ? 0 : -1}
        disabled={busy} onClick={() => { setTab(item); setMessage(null) }}
        onKeyDown={(event) => {
          if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
          event.preventDefault()
          const next = event.key === 'Home' ? 'extracted' : event.key === 'End' ? 'entered'
            : tab === 'extracted' ? 'entered' : 'extracted'
          setTab(next)
          document.getElementById(`project-data-tab-${next}`)?.focus()
        }}>
        {item === 'extracted' ? 'Dati estratti' : 'Dati inseriti'}
        {item === 'entered' && dirty ? ' *' : ''}
      </button>)}
    </div>
    {error && <div className="knowledge-error" role="alert">{error}
      {!review && !loading && <button type="button" className="button" onClick={() => setReload((n) => n + 1)}>Riprova</button>}
    </div>}
    <section id="project-data-extracted" role="tabpanel" aria-labelledby="project-data-tab-extracted" hidden={tab !== 'extracted'}>
      <div className="project-facts-toolbar">
        <h3>Informazioni dalle fonti</h3>
        <button className="button" type="button" disabled={busy || loading || !review || !saved.editable} onClick={extract}>
          <WandSparkles size={16} />{operation === 'extract' ? 'Estrazione in corso' : review?.facts.length ? 'Riestrai dalle fonti' : 'Estrai dalle fonti'}
        </button>
      </div>
      <CallFactsReviewPanel projectId={projectId} review={review} loading={loading}
        disabled={Boolean(operation) || loading || !saved.editable} onDirtyChange={setFactDirty}
        onError={setError} onUpdated={(updated, feedback) => {
          setReview(updated)
          onUpdated(updated.artifact)
          setMessage(feedback)
        }} />
    </section>
    <section id="project-data-entered" role="tabpanel" aria-labelledby="project-data-tab-entered" hidden={tab !== 'entered'}>
      <label className="project-facts-label" htmlFor="project-entered-data">Dati e scelte del proponente</label>
      <textarea id="project-entered-data" className="markdown-editor project-facts-editor"
        value={content} maxLength={50000} readOnly={!saved.editable || Boolean(operation)}
        onChange={(event) => { setContent(event.target.value); setMessage(null) }} />
      <footer className="artifact-editor-footer">
        <span>{dirty ? 'Modifiche non salvate' : 'Salvato'}</span>
        <div className="artifact-actions">
          {dirty && <button className="button" type="button" disabled={busy} onClick={() => {
            if (window.confirm('Annullare le modifiche non salvate?')) setContent(saved.content)
          }}>Annulla modifiche</button>}
          <button className="button button--primary" type="button" disabled={busy || !dirty || !content.trim() || !saved.editable} onClick={save}>
            <Save size={16} />{operation === 'save' ? 'Salvataggio' : 'Salva dati'}
          </button>
        </div>
      </footer>
    </section>
    <div className="project-facts-feedback" role="status">{message}</div>
  </div>
}
