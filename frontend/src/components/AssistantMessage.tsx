import { LoaderCircle } from 'lucide-react'
import type { ReactNode } from 'react'

export function AssistantMessage({ id, model, busy = false, error, children }: {
  id: string
  model?: string | null
  busy?: boolean
  error?: string | null
  children?: ReactNode
}) {
  return <section className="grounded-answer" aria-labelledby={`${id}-title`} aria-busy={busy}>
    <div className="grounded-answer-heading">
      <h2 id={`${id}-title`}>Risposta Mapi</h2>
      {model && <span>{model}</span>}
    </div>
    {children}
    {busy && <p className="assistant-activity" role="status" aria-label="Mapi sta elaborando">
      <LoaderCircle size={16} aria-hidden="true" />
      <span>Sto lavorando…</span>
    </p>}
    {error && <p role="alert">{error}</p>}
  </section>
}
