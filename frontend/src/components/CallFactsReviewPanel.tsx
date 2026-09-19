import { FileText, Pencil, RotateCcw, Save, Trash2, X } from 'lucide-react'
import { useEffect, useMemo, useState } from 'react'
import { api } from '../api'
import type {
  CallFactAction,
  CallFactItem,
  CallFactsReview,
} from '../types'
import { LoadingState } from './LoadingState'
import { StatusPill } from './StatusPill'

type FactFilter = 'active' | 'discarded'
type EditAction = Exclude<CallFactAction, 'verify'>

interface CallFactsReviewPanelProps {
  projectId: string
  review: CallFactsReview | null
  loading: boolean
  onUpdated: (review: CallFactsReview, message: string) => void
  onError: (message: string | null) => void
  disabled?: boolean
  onDirtyChange: (dirty: boolean) => void
}

export function CallFactsReviewPanel({
  projectId,
  review,
  loading,
  onUpdated,
  onError,
  disabled = false,
  onDirtyChange,
}: CallFactsReviewPanelProps) {
  const [filter, setFilter] = useState<FactFilter>('active')
  const [workingId, setWorkingId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editValue, setEditValue] = useState('')
  useEffect(() => {
    onDirtyChange(Boolean(editingId || workingId))
    return () => onDirtyChange(false)
  }, [editingId, workingId, onDirtyChange])

  const filteredFacts = useMemo(() => {
    if (!review) return []
    return review.facts.filter((fact) => filter === 'active'
      ? fact.status !== 'discarded' : fact.status === 'discarded')
  }, [filter, review])

  if (loading) return <LoadingState label="Caricamento dati estratti" />
  if (!review) {
    return <div className="fact-empty-state">Dati estratti non disponibili.</div>
  }

  const filters: Array<{ id: FactFilter; label: string; count: number }> = [
    { id: 'active', label: 'Attivi', count: review.facts.length - review.discarded_count },
    { id: 'discarded', label: 'Esclusi', count: review.discarded_count },
  ]

  async function revise(
    fact: CallFactItem,
    action: EditAction,
    fields?: { title: string; value: string },
  ) {
    if (!review || disabled || workingId) return
    setWorkingId(fact.id)
    onError(null)
    try {
      const updated = await api.reviseCallFact(projectId, fact.id, {
        action,
        version: review.artifact.version,
        ...fields,
      })
      setEditingId(null)
      const messages: Record<EditAction, string> = {
        edit: `“${fact.title}” aggiornato.`,
        discard: `“${fact.title}” escluso dai dati estratti.`,
        restore: `“${fact.title}” ripristinato.`,
      }
      onUpdated(updated, messages[action])
    } catch (reason) {
      onError(reason instanceof Error ? reason.message : 'Revisione non riuscita')
    } finally {
      setWorkingId(null)
    }
  }

  function startEditing(fact: CallFactItem) {
    setEditingId(fact.id)
    setEditTitle(fact.title)
    setEditValue(fact.value)
    onError(null)
  }

  return (
    <div className="call-facts-review">
      <div className="fact-filter-tabs" role="group" aria-label="Filtra dati estratti">
        {filters.map((item) => (
          <button
            className={filter === item.id ? 'is-active' : ''}
            type="button"
            aria-pressed={filter === item.id}
            disabled={disabled || Boolean(editingId || workingId)}
            key={item.id}
            onClick={() => setFilter(item.id)}
          >
            {item.label} <span>{item.count}</span>
          </button>
        ))}
      </div>

      {review.missing_information.length > 0 && (
        <details className="fact-missing-banner">
          <summary>Informazioni non trovate ({review.missing_information.length})</summary>
          <ul>
            {review.missing_information.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </details>
      )}

      <div className="call-fact-list">
        {filteredFacts.length === 0 ? (
          <div className="fact-empty-state">{filter === 'active' ? 'Nessun dato estratto.' : 'Nessun dato escluso.'}</div>
        ) : filteredFacts.map((fact, index) => {
          const editing = editingId === fact.id
          const working = workingId === fact.id
          return (
            <article
              className={`call-fact-row${fact.status === 'discarded' ? ' is-discarded' : ''}`}
              key={fact.id}
            >
              <header className="call-fact-heading">
                <div>
                  <span className="section-label">Dato {index + 1}</span>
                  <h3>{fact.title}</h3>
                </div>
                <StatusPill tone={fact.status === 'discarded' ? 'purple' : 'info'}>
                  {fact.status === 'discarded' ? 'Escluso' : fact.origin === 'user_corrected' ? 'Corretto' : 'Estratto'}
                </StatusPill>
              </header>

              {editing ? (
                <form
                  className="call-fact-edit"
                  onSubmit={(event) => {
                    event.preventDefault()
                    void revise(fact, 'edit', { title: editTitle, value: editValue })
                  }}
                >
                  <label>
                    Titolo
                    <input
                      value={editTitle}
                      maxLength={180}
                      required
                      onChange={(event) => setEditTitle(event.target.value)}
                    />
                  </label>
                  <label>
                    Valore
                    <textarea
                      value={editValue}
                      maxLength={4000}
                      required
                      onChange={(event) => setEditValue(event.target.value)}
                    />
                  </label>
                  <div className="call-fact-actions">
                    <button
                      className="button button--compact"
                      type="button"
                      disabled={working}
                      onClick={() => setEditingId(null)}
                    >
                      <X size={15} /> Annulla
                    </button>
                    <button
                      className="button button--primary button--compact"
                      type="submit"
                      disabled={working || !editTitle.trim() || !editValue.trim()}
                    >
                      <Save size={15} /> {working ? 'Salvataggio' : 'Salva modifica'}
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <p className="call-fact-value">{fact.value}</p>
                  <div className="call-fact-sources">
                    <span>{fact.origin === 'user_corrected' ? 'Fonte di origine' : 'Provenienza'}</span>
                    <ul>
                      {fact.sources.map((source) => (
                        <li key={`${source.name}-${source.fragment}`}>
                          <FileText size={14} />
                          {source.name}, frammento {source.fragment}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <footer className="call-fact-actions">
                    {fact.status !== 'discarded' && (
                      <button
                        className="button button--compact"
                        type="button"
                        disabled={disabled || Boolean(editingId || workingId)}
                        onClick={() => startEditing(fact)}
                      >
                        <Pencil size={15} /> Modifica
                      </button>
                    )}
                    {fact.status !== 'discarded' ? (
                      <button
                        className="button button--compact fact-discard"
                        type="button"
                        disabled={disabled || Boolean(editingId || workingId)}
                        onClick={() => void revise(fact, 'discard')}
                      >
                        <Trash2 size={15} /> Escludi
                      </button>
                    ) : (
                      <button
                        className="button button--compact"
                        type="button"
                        disabled={disabled || Boolean(editingId || workingId)}
                        onClick={() => void revise(fact, 'restore')}
                      >
                        <RotateCcw size={15} /> Ripristina
                      </button>
                    )}
                  </footer>
                </>
              )}
            </article>
          )
        })}
      </div>
    </div>
  )
}
