import { useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'
import { AppShell } from '../components/AppShell'
import { ErrorState, LoadingState } from '../components/LoadingState'
import { StatusPill } from '../components/StatusPill'
import { useProject } from '../hooks/useProject'
import type { DocumentReview } from '../types'

interface ReviewState {
  requestedId?: string
  review: DocumentReview | null
  error: string | null
}

export function DocumentReviewPage() {
  const { projectId } = useParams()
  const { project, loading: projectLoading, error: projectError } = useProject(projectId)
  const [state, setState] = useState<ReviewState>({ review: null, error: null })
  const review = state.requestedId === projectId ? state.review : null
  const error = state.requestedId === projectId ? state.error : null

  useEffect(() => {
    if (!projectId) return
    const controller = new AbortController()
    setState({ requestedId: projectId, review: null, error: null })
    api
      .documentReview(projectId, controller.signal)
      .then((result) => {
        if (controller.signal.aborted) return
        setState({ requestedId: projectId, review: result, error: null })
      })
      .catch((reason: Error) => {
        if (controller.signal.aborted || reason.name === 'AbortError') return
        setState({ requestedId: projectId, review: null, error: reason.message })
      })
    return () => controller.abort()
  }, [projectId])

  const sections = useMemo(() => {
    if (!review) return []
    return Array.from(new Set(review.fields.map((field) => field.section))).map((section) => ({
      section,
      fields: review.fields.filter((field) => field.section === section),
    }))
  }, [review])

  if (projectError || error || (!projectLoading && !project)) {
    return <AppShell active="documents"><ErrorState message={projectError ?? error ?? 'Documento non trovato'} /></AppShell>
  }
  if (projectLoading || !project || !review) {
    return <AppShell active="documents" project={project}><LoadingState /></AppShell>
  }

  const percentage = review.total_fields > 0
    ? Math.round((review.completed_fields / review.total_fields) * 100)
    : 0
  const missing = review.fields.filter((field) => field.status === 'missing')
  const provenance = review.fields.reduce<Record<string, number>>((counts, field) => {
    counts[field.source_kind] = (counts[field.source_kind] ?? 0) + 1
    return counts
  }, {})

  return (
    <AppShell active="documents" project={project} contentClassName="review-content">
      <Link className="back-link" to={`/projects/${project.id}`}>← {project.title}</Link>
      <header className="review-heading">
        <div>
          <h1>{review.title}</h1>
          <p>Esempio di revisione · {review.completed_fields} campi su {review.total_fields} compilati</p>
        </div>
        <StatusPill tone="info">Demo</StatusPill>
        <div className="review-actions">
          <Link className="button" to={`/projects/${project.id}?documents=docx`}>Apri moduli e bozze</Link>
        </div>
      </header>

      <div className="review-layout">
        <article className="document-preview">
          <span className="document-eyebrow">Dati dimostrativi</span>
          <h2>Anteprima dimostrativa</h2>
          <p>{project.title}</p>
          <div className="document-rule" />
          {sections.map(({ section, fields }, sectionIndex) => (
            <section className="document-section" key={section}>
              <h3>{sectionIndex + 1}. {section}</h3>
              {fields.map((field) => (
                <div className={`document-field${field.status === 'missing' ? ' document-field--missing' : ''}`} key={field.id}>
                  <span>{field.label}</span>
                  <div>
                    <strong>{field.value ?? 'Informazione mancante'}</strong>
                    <small>{field.provenance}</small>
                  </div>
                  <StatusPill tone={field.status === 'missing' ? 'warning' : 'success'}>
                    {field.status === 'missing' ? 'Dato utente' : 'Verificato'}
                  </StatusPill>
                </div>
              ))}
            </section>
          ))}
          <p className="document-note">
            Questa anteprima mostra dati dimostrativi e non permette modifiche.
            Le compilazioni e i report sono disponibili in Moduli e bozze nella vista del progetto.
          </p>
        </article>

        <aside className="review-panel">
          <h2>Stato del documento</h2>
          <strong className="completion-label">{percentage}% completato</strong>
          <div className="progress-track"><span style={{ width: `${percentage}%` }} /></div>
          <div className="review-summary">
            <strong>{review.completed_fields} completati</strong>
            <strong>{review.total_fields - review.completed_fields} mancanti</strong>
          </div>
          <span className="section-label">Elementi da verificare</span>
          {missing.map((field) => (
            <div className="review-warning" key={field.id}>
              <strong>{field.label}</strong>
              <span>Richiesto dal modello · nessuna fonte</span>
            </div>
          ))}
          <span className="section-label">Provenienza dei campi</span>
          <div className="provenance-list">
            <div><span className="source-dot source-dot--success" />Dati aziendali <em>{provenance.company ?? 0} campi</em></div>
            <div><span className="source-dot source-dot--info" />Dati del bando <em>{provenance.call ?? 0} campi</em></div>
            <div><span className="source-dot source-dot--purple" />Dati del progetto <em>{provenance.project ?? 0} campi</em></div>
          </div>
          <div className="human-review-note">L'approvazione finale spetta al revisore umano.</div>
        </aside>
      </div>
    </AppShell>
  )
}
