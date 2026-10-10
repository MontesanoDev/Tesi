import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import { compilationReplyParagraphs } from '../compilationReply'
import type { CompilationSession, GroundedAnswer } from '../types'

export function CompilationReply({ session, response, pending, processing, locked, error, onRetry }: {
  session: CompilationSession
  response?: GroundedAnswer | null
  pending: boolean
  processing: boolean
  locked: boolean
  error: string | null
  onRetry: () => void
}) {
  const [downloading, setDownloading] = useState(false)
  const [downloadError, setDownloadError] = useState<string | null>(null)
  const downloadController = useRef<AbortController | null>(null)
  useEffect(() => () => downloadController.current?.abort(), [])

  const paragraphs = compilationReplyParagraphs(session, response, processing, error)

  async function download() {
    if (!session.last_generation || downloadController.current) return
    const controller = new AbortController()
    downloadController.current = controller
    setDownloading(true)
    setDownloadError(null)
    try {
      const blob = await api.downloadCompilation(session.project_id, session.last_generation.id, 'docx', controller.signal)
      if (controller.signal.aborted) return
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = session.template_name.replace(/\.docx$/i, '.compilato.docx')
      link.click()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch {
      if (!controller.signal.aborted) setDownloadError('Non riesco a scaricare la bozza. Puoi riprovare: il documento è conservato.')
    } finally {
      if (!controller.signal.aborted) setDownloading(false)
      if (downloadController.current === controller) downloadController.current = null
    }
  }

  if (pending) return null
  return <>
    {paragraphs.map((paragraph, index) => <p key={index}>{paragraph}</p>)}
    {(error || session.last_error) && <p role="alert">{error
      || 'Ho conservato il lavoro fatto finora, ma non sono riuscito a completare il modulo. Possiamo riprendere o preparare una bozza parziale.'}</p>}
    {error && <button type="button" className="button" disabled={locked} onClick={onRetry}>Riprova</button>}
    {session.last_generation && <>
      {session.open_issues.length > 0
        ? <p>Ho preparato una bozza parziale: restano informazioni da chiarire per completare il modulo.</p>
        : !paragraphs.length && <p>Ho preparato la bozza. Puoi scaricarla e verificarla.</p>}
      {session.version > session.last_generation.session_version + 1
        && <p>La copia scaricabile precede le ultime modifiche. Chiedimi di generare una nuova copia per includerle.</p>}
      <div className="assistant-attachment">
        <button type="button" className="button" disabled={locked || downloading} onClick={() => void download()}>
          {downloading ? 'Scarico il documento…' : 'Scarica DOCX'}
        </button>
      </div>
    </>}
    {downloadError && <p role="alert">{downloadError}</p>}
  </>
}
