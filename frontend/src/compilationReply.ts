import type { CompilationSession, GroundedAnswer } from './types'

// The same paragraphs are displayed live and retained when the next turn starts.
export function compilationReplyParagraphs(session: CompilationSession,
  response: GroundedAnswer | null | undefined, processing: boolean, error: string | null) {
  if (session.engine === 'legacy') return [response?.answer,
    'Questa sessione usa il motore precedente. Per provare la compilazione globale, apri una nuova conversazione e seleziona il modulo con @.'].filter((text): text is string => Boolean(text))
  if (session.engine === 'global') {
    if (response && response.compilation?.session_id !== session.id) return [response.answer]
    if (processing) return ['Analizzo l’intero modulo e verifico le informazioni disponibili…']
    if (session.chat?.paused_by_user) return ['La compilazione è in pausa. Chiedimi di riprendere quando vuoi.']
    if (error || session.last_error || session.chat?.paused) return ['Ho conservato il lavoro. Chiedimi di riprendere per ritentare l’analisi.']
    if (session.global_compilation?.phase === 'REVIEW') return [session.last_generation
      ? 'Ho preparato una bozza parziale con i valori che hai selezionato. Puoi scaricarla e verificarla.'
      : `Ho preparato ${session.global_compilation.proposal_count} ${session.global_compilation.proposal_count === 1 ? 'proposta' : 'proposte'} di valore dalle fonti. Rivedile prima di generare una bozza.`]
    return ['Preparo l’analisi globale del modulo…']
  }
  const ownsResponse = response?.compilation?.session_id === session.id
  const paused = ownsResponse && response?.compilation?.action === 'paused'
    || !processing && Boolean(session.chat?.paused || session.status === 'FAILED'
      || session.status === 'ANALYZING' || error)
  const question = !paused && (!response || ownsResponse) ? session.chat?.question?.message : null
  const answer = ownsResponse && response?.compilation?.action === 'start' && !processing
    && (question || paused || session.last_generation) ? '' : response?.answer
  const paragraphs: string[] = []
  if (answer) paragraphs.push(answer)
  if (processing && !answer) paragraphs.push('Analizzo il modulo e verifico le informazioni disponibili.')
  if (!processing && question && !answer?.includes(question)) paragraphs.push(question)
  if (!processing && !answer && paused && !error && !session.last_error) paragraphs.push(
    session.chat?.paused_by_user
      ? 'Va bene, mi fermo qui. Quando vuoi, chiedimi di riprendere.'
      : 'Ho conservato il lavoro fatto finora. Chiedimi di riprendere quando vuoi proseguire.',
  )
  return paragraphs
}
