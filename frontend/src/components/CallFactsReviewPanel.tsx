import { Check, FileText, Pencil, RotateCcw, Save, Trash2, X } from 'lucide-react'
import { useMemo, useState } from 'react'
import { api } from '../api'
import type {
  CallFactAction,
  CallFactItem,
  CallFactsReview,
  CallFactStatus,
  StatusTone,
} from '../types'
import { LoadingState } from './LoadingState'
import { StatusPill } from './StatusPill'

type FactFilter = 'pending' | 'verified' | 'discarded' | 'all'

interface CallFactsReviewPanelProps {
  projectId: string
  review: CallFactsReview | null
  loading: boolean
  onUpdated: (review: CallFactsReview, message: string) => void
  onError: (message: string | null) => void
}

const STATUS: Record<CallFactStatus, { label: string; tone: StatusTone }> = {
  pending: { label: 'Da verificare', tone: 'warning' },
  verified: { label: 'Verificato', tone: 'success' },
  discarded: { label: 'Scartato', tone: 'purple' },
}

export function CallFactsReviewPanel({
  projectId,
  review,
  loading,
  onUpdated,
  onError,
}: CallFactsReviewPanelProps) {
  const [filter, setFilter] = useState<FactFilter>('pending')
  const [workingId, setWorkingId] = useState<string | null>(null)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editTitle, setEditTitle] = useState('')
  const [editValue, setEditValue] = useState('')

  const filteredFacts = useMemo(() => {
    if (!review) return []
    return filter === 'all'
      ? review.facts
      : review.facts.filter((fact) => fact.status === filter)
  }, [filter, review])

  if (loading) return <LoadingState label="Caricamento revisione" />
  if (!review) {
    return <div className="fact-empty-state">Revisione non disponibile.</div>
  }

  const filters: Array<{ id: FactFilter; label: string; count: number }> = [
    { id: 'pending', label: 'Da verificare', count: review.pending_count },
    { id: 'verified', label: 'Verificati', count: review.verified_count },
    { id: 'discarded', label: 'Scartati', count: review.discarded_count },
    { id: 'all', label: 'Tutti', count: review.facts.length },
  ]

  async function revise(
    fact: CallFactItem,
    action: CallFactAction,
    fields?: { title: string; value: string },
  ) {
    if (!review) return
    setWorkingId(fact.id)
    onError(null)
    try {
      const updated = await api.reviseCallFact(projectId, fact.id, {
        action,
        version: review.artifact.version,
        ...fields,
      })
      setEditingId(null)
      const messages: Record<CallFactAction, string> = {
        verify: `“${fact.title}” verificato e reso disponibile al RAG.`,
        edit: `“${fact.title}” modificato e rimesso in verifica.`,
        discard: `“${fact.title}” scartato e rimosso dalla conoscenza utilizzabile.`,
        restore: `“${fact.title}” ripristinato tra i fatti da verificare.`,
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
      <div className="call-facts-summary" aria-label="Stato revisione Call Facts">
        <div><strong>{review.pending_count}</strong><span>Da verificare</span></div>
        <div><strong>{review.verified_count}</strong><span>Verificati</span></div>
        <div><strong>{review.discarded_count}</strong><span>Scartati</span></div>
      </div>

      <div className="fact-filter-tabs" role="tablist" aria-label="Filtra Call Facts">
        {filters.map((item) => (
          <button
            className={filter === item.id ? 'is-active' : ''}
            type="button"
            role="tab"
            aria-selected={filter === item.id}
            key={item.id}
            onClick={() => setFilter(item.id)}
          >
            {item.label} <span>{item.count}</span>
          </button>
        ))}
      </div>

      {review.missing_information.length > 0 && (
        <div className="fact-missing-banner">
          <strong>Informazioni mancanti</strong>
          <ul>
            {review.missing_information.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>
      )}

      <div className="call-fact-list">
        {filteredFacts.length === 0 ? (
          <div className="fact-empty-state">Nessun fatto in questo stato.</div>
        ) : filteredFacts.map((fact, index) => {
          const status = STATUS[fact.status]
          const editing = editingId === fact.id
          const working = workingId === fact.id
          return (
            <article
              className={`call-fact-row${fact.status === 'discarded' ? ' is-discarded' : ''}`}
              key={fact.id}
            >
              <header className="call-fact-heading">
                <div>
                  <span className="section-label">Fatto {index + 1}</span>
                  <h3>{fact.title}</h3>
                </div>
                <StatusPill tone={status.tone}>{status.label}</StatusPill>
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
                    <span>Provenienza</span>
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
                    {fact.status === 'pending' && (
                      <button
                        className="button button--primary button--compact"
                        type="button"
                        disabled={working}
                        onClick={() => void revise(fact, 'verify')}
                      >
                        <Check size={15} /> {working ? 'Salvataggio' : 'Verifica'}
                      </button>
                    )}
                    {fact.status !== 'discarded' && (
                      <button
                        className="button button--compact"
                        type="button"
                        disabled={working}
                        onClick={() => startEditing(fact)}
                      >
                        <Pencil size={15} /> Modifica
                      </button>
                    )}
                    {fact.status !== 'discarded' ? (
                      <button
                        className="button button--compact fact-discard"
                        type="button"
                        disabled={working}
                        onClick={() => void revise(fact, 'discard')}
                      >
                        <Trash2 size={15} /> Scarta
                      </button>
                    ) : (
                      <button
                        className="button button--compact"
                        type="button"
                        disabled={working}
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
