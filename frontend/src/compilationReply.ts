import type { CompilationSession, GroundedAnswer } from './types'

// The same paragraphs are displayed live and retained when the next turn starts.
export function compilationReplyParagraphs(session: CompilationSession,
  response: GroundedAnswer | null | undefined, processing: boolean, error: string | null) {
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
