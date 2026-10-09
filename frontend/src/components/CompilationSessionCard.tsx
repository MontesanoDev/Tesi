import { useEffect, useRef, useState, type FormEvent } from 'react'
import { LoaderCircle } from 'lucide-react'
import { api } from '../api'
import type { CompilationFieldInput, CompilationFieldStatus, CompilationSession, CompilationSessionField } from '../types'
import './CompilationSessionCard.css'

const fieldStatus: Record<CompilationFieldStatus, string> = {
  PENDING: 'Da analizzare', RESOLVED: 'Verificato da fonte', MISSING: 'Mancante',
  AMBIGUOUS: 'Ambiguo', CONFLICTING: 'Fonti in conflitto', NOT_APPLICABLE: 'Non applicabile',
  USER_PROVIDED: 'Fornito dall’utente',
}
const sessionStatus = {
  CREATED: 'Pronta per l’analisi', ANALYZING: 'Elaborazione in corso', WAITING_FOR_USER: 'In attesa di informazioni',
  READY: 'Pronta per la generazione', GENERATED: 'Bozza disponibile', FAILED: 'Compilazione in pausa',
}
const counts = {
  total: 'Candidate totali', pending: 'Da analizzare', resolved: 'Verificati da fonte', missing: 'Mancanti',
  ambiguous: 'Ambigui', conflicting: 'In conflitto', not_applicable: 'Non applicabili', user_provided: 'Forniti dall’utente',
} as const

interface Props {
  session: CompilationSession
  busy: boolean
  processing: boolean
  loading: boolean
  error: string | null
  questionInChat?: boolean
  onContinue: (ids?: string[]) => Promise<CompilationSession | null>
  onUpdate: (field: CompilationFieldInput) => Promise<CompilationSession | null>
  onGenerate: (draft?: boolean) => Promise<CompilationSession | null>
  onRefresh: () => void
  onResume: () => void
}

function labelOf(field: CompilationSessionField) {
  const name = field.requirement?.name || field.label || field.id
  return field.requirement?.person_role ? `${name} · ${field.requirement.person_role}` : name
}

export function CompilationSessionCard({ session, busy, processing, loading, error, questionInChat = false, onContinue, onUpdate, onGenerate, onRefresh, onResume }: Props) {
  const [detailsOpen, setDetailsOpen] = useState(false)
  const [editing, setEditing] = useState<string | null>(null)
  const [value, setValue] = useState('')
  const [reason, setReason] = useState('')
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState<string | null>(null)
  const downloadController = useRef<AbortController | null>(null)
  useEffect(() => () => downloadController.current?.abort(), [])
  const locked = busy || processing || loading
  const paused = !processing && (session.chat?.paused || session.status === 'FAILED'
    || session.status === 'ANALYZING' || Boolean(error))
  const resumable = paused || (!session.chat?.enabled && session.summary.pending > 0)
  const draftAvailable = session.status === 'GENERATED' && Boolean(session.last_generation)
  const statusLabel = processing ? 'Elaborazione in corso'
    : draftAvailable ? 'Bozza disponibile' : paused ? 'Compilazione in pausa' : sessionStatus[session.status]
  const selected = session.fields.find((field) => field.id === editing)
  const openFields = session.open_issues.filter((issue) => issue.status !== 'PENDING')
  const decided = session.fields.filter((field) => !['PENDING', 'MISSING', 'AMBIGUOUS', 'CONFLICTING'].includes(field.status))

  function edit(field: CompilationSessionField) {
    setEditing(field.id)
    setValue(field.value ?? '')
    setReason('')
  }
  async function update(action: CompilationFieldInput['action']) {
    if (!selected || locked) return
    const result = await onUpdate({ field_id: selected.id, action,
      ...(action === 'set' ? { value } : action === 'not_applicable' ? { reason } : {}) })
    if (result) setEditing(null)
  }
  function save(event: FormEvent) { event.preventDefault(); void update('set') }

  async function download(kind: 'docx' | 'report') {
    if (!session.last_generation || downloadController.current) return
    const controller = new AbortController()
    downloadController.current = controller
    setDownloading(true)
    setDownloadError(null)
    try {
      const blob = await api.downloadCompilation(session.project_id, session.last_generation.id, kind, controller.signal)
      if (controller.signal.aborted) return
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = kind === 'docx' ? session.template_name.replace(/\.docx$/i, '.compilato.docx') : `${session.template_name}.report.json`
      link.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (err) {
      if (!controller.signal.aborted) {
        console.warn('Download CompilationSession', err)
        setDownloadError('Non riesco a scaricare la bozza. I dati sono conservati: puoi riprovare.')
      }
    } finally {
      if (!controller.signal.aborted) setDownloading(false)
      if (downloadController.current === controller) downloadController.current = null
    }
  }

  function fieldRow(field: CompilationSessionField) {
    return <li key={field.id}>
      <div className="compilation-field-heading">
        <span><strong>{labelOf(field)}</strong> — {fieldStatus[field.status]}</span>
        <button type="button" className="button" disabled={locked} onClick={() => edit(field)}
          aria-label={`${field.value ? 'Correggi' : 'Chiarisci'} ${labelOf(field)}`}>
          {field.value ? 'Correggi' : 'Chiarisci'}
        </button>
      </div>
      {field.value && <p>{field.value}</p>}
      {field.reason && <p className="compilation-note">{field.reason}</p>}
      {field.provenance === 'USER' && <p className="compilation-note">USER · Indicazione dell’utente, non verificata da una fonte.</p>}
      {field.validation_errors.length > 0 && <p>{field.validation_errors.join(' · ')}</p>}
      <details className="compilation-evidence">
        <summary>Requisito e provenienza</summary>
        <p>FORM · {field.form_evidence.source_name} · {field.candidate_id}</p>
        <blockquote>{field.requirement?.form_quote || field.form_evidence.quote || field.label}</blockquote>
        {field.source_evidence.map((evidence, index) => <div key={`${evidence.chunk_id}-${index}`}>
          <p>SOURCE · {evidence.source_name} · {evidence.project_id ? 'Progetto' : evidence.category === 'company' ? 'Company KB' : evidence.category === 'general' ? 'General KB' : evidence.scope || 'Fonte globale'}</p>
          <blockquote>{evidence.quote}</blockquote>
        </div>)}
        {field.alternatives.map((item, index) => <p key={index}>Alternativa: {item.value} — SOURCE · {item.evidence.source_name}</p>)}
      </details>
    </li>
  }

  return <section className="compilation-chat-card" aria-label={`Compilazione ${session.template_name}`} aria-busy={processing || loading}>
    <header><strong>Compilazione · {session.template_name}</strong><span role="status">{statusLabel}</span></header>
    <div className="compilation-conversation" aria-live="polite">
      {!processing && session.chat?.notice && <p>{session.chat.notice}</p>}
      {processing && <p className="compilation-activity">
        <LoaderCircle size={16} aria-hidden="true" />
        Verifico le informazioni nelle fonti e completo i campi supportati…
      </p>}
      <p className="compilation-note">
        Ho verificato {session.summary.resolved} {session.summary.resolved === 1 ? 'informazione' : 'informazioni'} nelle fonti.
        {session.summary.user_provided > 0 && ` ${session.summary.user_provided} ${session.summary.user_provided === 1 ? 'valore è stato fornito' : 'valori sono stati forniti'} da te.`}
      </p>
      {!processing && !paused && !questionInChat && session.chat?.question &&
        <p className="compilation-question">{session.chat.question.message}</p>}
      {!processing && !paused && session.status === 'WAITING_FOR_USER' && Boolean(session.chat?.question?.field_ids.length) &&
        <p className="compilation-note">Rispondimi qui nella chat. La tua indicazione resterà distinta dai dati verificati nelle fonti.</p>}
      {draftAvailable && <p>{session.open_issues.length > 0
        ? 'È disponibile una bozza parziale. Restano informazioni da chiarire prima di completare il modulo.'
        : 'La bozza è disponibile. Puoi scaricarla e verificarla.'}</p>}
      {resumable && !draftAvailable && !error &&
          <p>{session.chat?.paused_by_user
            ? 'La compilazione è in pausa. Potrai riprenderla quando vuoi.'
            : 'I dati già verificati sono conservati. Puoi proseguire la compilazione dal punto raggiunto.'}</p>}
    </div>
    {(error || session.last_error) && <p role="alert" className="upload-feedback--error">
      {error || 'Ho conservato i dati già verificati. Alcuni campi non sono stati completati. Puoi continuare o esportare una bozza parziale.'}
    </p>}
    {(!processing || error) && <div className="compilation-primary-action">
      {error ? <button type="button" className="button button--primary" disabled={busy || loading} onClick={onRefresh}>Aggiorna stato</button>
        : draftAvailable ? <button type="button" className="button button--primary" disabled={locked || downloading}
          onClick={() => void download('docx')}>Scarica DOCX</button>
        : resumable ? <button type="button" className="button button--primary" disabled={locked} onClick={onResume}>Prosegui compilazione</button>
        : session.status === 'READY' && session.open_issues.length === 0 ? <button type="button" className="button button--primary" disabled={locked}
          onClick={() => void onGenerate()}>Genera DOCX</button> : null}
    </div>}
    <details className="compilation-debug" onToggle={(event) => setDetailsOpen(event.currentTarget.open)}>
      <summary>Dettagli compilazione</summary>
      {detailsOpen && <>
    <dl className="compilation-counts" aria-label="Stato della compilazione">
      {Object.entries(counts).map(([key, label]) => <div key={key}>
        <dt>{label}</dt><dd>{session.summary[key as keyof typeof counts]}</dd>
      </div>)}
    </dl>
    {session.summary.pending > 0 && <p className="compilation-note">Le posizioni da analizzare non sono ancora campi confermati. Ogni step analizza fino a 12 candidate.</p>}
    <div className="compilation-actions">
      {draftAvailable && resumable && <button type="button" className="button" disabled={locked}
        onClick={onResume}>Riprendi compilazione</button>}
      {session.summary.pending > 0 &&
        <button type="button" className="button" disabled={locked} onClick={() => void onContinue()}>Continua analisi</button>}
      {!error && <button type="button" className="button" disabled={busy || loading} onClick={onRefresh}>Aggiorna stato</button>}
    </div>
    {openFields.length > 0 && <details className="compilation-issues">
      <summary>Informazioni da chiarire ({openFields.length})</summary>
      <ul>{openFields.map((issue) => session.fields.find((field) => field.id === issue.field_id)).filter((f): f is CompilationSessionField => Boolean(f)).map(fieldRow)}</ul>
    </details>}
    {decided.length > 0 && <details className="compilation-issues">
      <summary>Valori e sezioni già valutati ({decided.length})</summary>
      <ul>{decided.map(fieldRow)}</ul>
    </details>}
    {selected && <form className="compilation-field-input" onSubmit={save} aria-label={`Aggiorna ${labelOf(selected)}`}>
      <strong>{labelOf(selected)}</strong>
      <label>Valore fornito dall’utente<textarea value={value} maxLength={1500} disabled={locked} onChange={(event) => setValue(event.target.value)} /></label>
      <div className="compilation-actions">
        <button type="submit" className="button" disabled={locked || !value.trim()}>Salva valore</button>
        <button type="button" className="button" disabled={locked} onClick={() => setEditing(null)}>Annulla</button>
        {['PENDING', 'MISSING', 'AMBIGUOUS', 'CONFLICTING'].includes(selected.status) &&
          <button type="button" className="button" disabled={locked} onClick={() => void onContinue([selected.id])}>Cerca nelle fonti</button>}
      </div>
      <details><summary>Non applicabile o da rivalutare</summary>
        <label>Motivo di non applicabilità<input value={reason} disabled={locked} onChange={(event) => setReason(event.target.value)} maxLength={1000} /></label>
        <div className="compilation-actions">
          <button type="button" className="button" disabled={locked || !reason.trim()} onClick={() => void update('not_applicable')}>Segna non applicabile</button>
          <button type="button" className="button" disabled={locked} onClick={() => void update('reset')}>Rimetti da analizzare</button>
        </div>
      </details>
    </form>}
    {session.open_issues.length > 0 && <button type="button" className="button" disabled={locked}
      onClick={() => void onGenerate(true)}>Genera bozza con campi irrisolti</button>}
    {session.last_generation && <p>Ultima bozza · versione {session.last_generation.session_version}</p>}
    {draftAvailable && session.open_issues.length === 0 && <button type="button" className="button" disabled={locked}
      onClick={() => void onGenerate()}>Genera nuova copia</button>}
    {session.last_generation && <button type="button" className="button" disabled={downloading}
      onClick={() => void download('report')}>Scarica report</button>}
      </>}
    </details>
    {session.last_generation && <div className="compilation-downloads">
      {session.version > session.last_generation.session_version + 1 &&
        <p>La copia scaricabile precede le ultime modifiche. Genera una nuova copia per includerle.</p>}
      {!draftAvailable && <div className="compilation-actions">
        <button type="button" className="button" disabled={downloading} onClick={() => void download('docx')}>Scarica DOCX</button>
      </div>}
    </div>}
    {downloadError && <p role="alert">{downloadError}</p>}
  </section>
}
