import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { compilationState } from '../compilationStatus'
import type { CompilationSession } from '../types'

function time(iso: string) {
  const date = new Date(iso)
  return Number.isNaN(date.getTime()) ? '' : date.toLocaleString('it-IT', {
    day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

// One persistent place for the exported drafts of a global compilation: the current state of the
// conversation is in the replies, the file is here, and nothing is exported without being asked.
export function CompilationDraftBar({ session, locked, onRequestDraft }: {
  session: CompilationSession
  locked: boolean
  onRequestDraft: () => void
}) {
  const [downloading, setDownloading] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const controller = useRef<AbortController | null>(null)
  useEffect(() => () => controller.current?.abort(), [])

  const draft = session.last_generation
  if (session.engine !== 'global' || !draft) return null
  const changed = draft.changes_since_export ?? session.version > draft.session_version + 1
  const earlier = session.draft_history ?? []

  async function download(id: string) {
    if (controller.current) return
    const current = new AbortController()
    controller.current = current
    setDownloading(id)
    setError(null)
    try {
      const blob = await api.downloadCompilation(session.project_id, id, 'docx', current.signal)
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
      if (!current.signal.aborted) setDownloading(null)
      if (controller.current === current) controller.current = null
    }
  }

  const state = compilationState(session)
  const created = time(draft.created_at)
  return <section className="compilation-draft-bar" aria-label="Ultima bozza esportata">
    <div>
      <p><strong>{state?.label ?? 'Compilazione DOCX · bozza'}</strong>{created && ` · esportata il ${created}`}</p>
      <p>Il DOCX è una bozza: va verificato prima dell’uso.</p>
      {changed && <p>Ci sono modifiche non ancora in questo file: chiedimi una nuova bozza per includerle.</p>}
    </div>
    <div className="compilation-draft-bar__actions">
      <button type="button" className="button" disabled={locked || Boolean(downloading)} onClick={() => void download(draft.id)}>
        {downloading === draft.id ? 'Scarico il documento…' : 'Scarica DOCX'}
      </button>
      {changed && <button type="button" className="button" disabled={locked} onClick={onRequestDraft}>Prepara nuova bozza</button>}
    </div>
    {earlier.length > 0 && <details>
      <summary>Bozze precedenti ({earlier.length})</summary>
      {earlier.map((item) => <button key={item.id} type="button" className="button" disabled={locked || Boolean(downloading)}
        onClick={() => void download(item.id)}>{downloading === item.id ? 'Scarico il documento…' : `Scarica la bozza del ${time(item.created_at)}`}</button>)}
    </details>}
    {error && <p role="alert">{error}</p>}
  </section>
}
