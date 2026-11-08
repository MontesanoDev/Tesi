import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { CompilationDraft } from '../compilationDrafts'
import type { CompilationSession } from '../types'

function time(iso: string) {
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('it-IT', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

export function CompilationDraftCard({ session, draft, locked, onRequestDraft }: {
  session: CompilationSession
  draft: CompilationDraft
  locked: boolean
  onRequestDraft: () => void
}) {
  const [downloading, setDownloading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const controller = useRef<AbortController | null>(null)
  useEffect(() => () => controller.current?.abort(), [])

  const latest = session.last_generation
  const changed = latest?.id === draft.id
    && (latest.changes_since_export ?? session.version > latest.session_version + 1)

  async function download() {
    if (controller.current) return
    const current = new AbortController()
    controller.current = current
    setDownloading(true)
    setError(null)
    try {
      const blob = await api.downloadCompilation(session.project_id, draft.id, 'docx', current.signal)
      if (current.signal.aborted) return
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = session.template_name.replace(/\.docx$/i, '.compilato.docx')
      link.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch {
      if (!current.signal.aborted) setError('Non riesco a scaricare il file. Puoi riprovare: il documento è conservato.')
    } finally {
      if (!current.signal.aborted) setDownloading(false)
      if (controller.current === current) controller.current = null
    }
  }

  const created = time(draft.created_at)
  return <section className="compilation-draft-card" aria-label={`Bozza ${draft.number} esportata`}>
    <div>
      <p><strong>Compilazione DOCX · bozza {draft.number}</strong>{created && ` · esportata il ${created}`}</p>
      <p>Il DOCX è una bozza: va verificato prima dell’uso.</p>
      {changed && <p>Ci sono modifiche non ancora in questo file: chiedimi una nuova bozza per includerle.</p>}
    </div>
    <div className="compilation-draft-card__actions">
      <button type="button" className="button" disabled={locked || downloading} onClick={() => void download()}>
        {downloading ? 'Scarico il documento…' : 'Scarica DOCX'}
      </button>
      {changed && <button type="button" className="button" disabled={locked} onClick={onRequestDraft}>Prepara nuova bozza</button>}
    </div>
    {error && <p role="alert">{error}</p>}
  </section>
}
