import type { CompilationChatAction, CompilationSession } from './types'

export interface CompilationDraft { id: string, created_at: string, number: number }
interface ConversationTurnRef { id: string, result?: { compilation?: CompilationChatAction | null } | null }

// Each export stays under the message that produced it: an ordinary message adds nothing, moves
// nothing and exports nothing. A draft no message claims (exported elsewhere) is listed once at the
// end of the conversation.
export function draftsOfConversation(session: CompilationSession | null | undefined, turns: ConversationTurnRef[]) {
  const byTurn = new Map<string, CompilationDraft>()
  const latest = session?.last_generation
  if (!session || session.engine !== 'global' || !latest) return { byTurn, unclaimed: [] as CompilationDraft[] }
  const drafts = [...(session.draft_history ?? []), latest]
    .map((draft, index) => ({ id: draft.id, created_at: draft.created_at, number: index + 1 }))
  const exports = turns.filter((turn) => turn.result?.compilation?.session_id === session.id
    && turn.result.compilation.action === 'generated')
  const free = [...drafts]
  const unnamed: ConversationTurnRef[] = []
  for (const turn of exports) {
    const id = turn.result?.compilation?.generation_id
    const index = free.findIndex((draft) => draft.id === id)
    if (index >= 0) byTurn.set(turn.id, free.splice(index, 1)[0])
    else if (!id) unnamed.push(turn)
  }
  // Messages stored before each export named its draft: the same order, from the first.
  for (const turn of unnamed) {
    const draft = free.shift()
    if (draft) byTurn.set(turn.id, draft)
  }
  return { byTurn, unclaimed: free }
}
