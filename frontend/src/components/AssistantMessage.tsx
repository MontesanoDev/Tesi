import { LoaderCircle } from 'lucide-react'
import type { ReactNode } from 'react'

export function AssistantMessage({ id, model, busy = false, error, children,
  activity = 'Sto lavorando…' }: {
  id: string
  model?: string | null
  busy?: boolean
  error?: string | null
  children?: ReactNode
  activity?: string
}) {
  return <section className="grounded-answer" aria-labelledby={`${id}-title`} aria-busy={busy}>
    <div className="grounded-answer-heading">
      <h2 id={`${id}-title`}>Risposta</h2>
      {model && <span>{model}</span>}
    </div>
    {children}
    {busy && <p className="assistant-activity" role="status" aria-label="Elaborazione in corso">
      <LoaderCircle size={16} aria-hidden="true" />
      <span>{activity}</span>
    </p>}
    {error && <p role="alert">{error}</p>}
  </section>
}
