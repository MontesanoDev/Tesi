import type { CompilationSession } from './types'

// «Compilazione DOCX»: real states read from the session, no invented progress percentages.
export const COMPILATION_NAME = 'Compilazione DOCX'

function failedSegments(session: CompilationSession) {
  return (session.global_compilation?.segments ?? []).filter((segment) => segment.status !== 'analyzed')
}

function time(iso: string) {
  return new Date(iso).toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' })
}

// Shown in the live status while a request is running.
export function compilationActivity(session?: CompilationSession | null) {
  if (!session) return `Avvio della ${COMPILATION_NAME}…`
  if (session.engine !== 'global') return 'Sto lavorando…'
  const data = session.global_compilation
  if (session.status === 'ANALYZING' || !data || data.phase !== 'REVIEW') {
    return 'Analisi del documento e compilazione delle sezioni…'
  }
  if (session.chat?.question?.kind === 'generate') return 'Preparazione del DOCX…'
  return 'Verifica dei dati…'
}

// Shown under the reply once nothing is running: the state and its honest limits.
export function compilationState(session: CompilationSession) {
  if (session.engine !== 'global') return null
  const data = session.global_compilation
  const notes: string[] = []
  let label: string
  if (session.status === 'ANALYZING' && session.lease_until && Date.parse(session.lease_until) > Date.now()) {
    label = 'compilazione in corso'
    notes.push(`Se il servizio è stato interrotto, potrai riprendere la compilazione dalle ${time(session.lease_until)}: `
      + 'le sezioni già validate restano conservate.')
  } else if (session.status === 'FAILED' || session.last_error) {
    label = 'compilazione interrotta'
  } else if (session.last_generation) {
    const incomplete = failedSegments(session).length > 0 || session.summary.pending > 0
    label = incomplete ? 'bozza incompleta' : 'bozza completata'
    notes.push('Il DOCX è una bozza: va verificato prima dell’uso.')
  } else if (data?.phase === 'REVIEW' && data.dialogue?.phase === 'READY') {
    label = session.chat?.question && session.chat.question.kind !== 'generate'
      ? 'attesa di chiarimenti' : 'verifica dei dati completata'
  } else {
    return null
  }
  if (failedSegments(session).length) {
    notes.unshift('Una parte del documento non è stata analizzata: i relativi campi restano vuoti '
      + 'e la compilazione è incompleta.')
  }
  return { label: `${COMPILATION_NAME} · ${label}`, notes }
}
