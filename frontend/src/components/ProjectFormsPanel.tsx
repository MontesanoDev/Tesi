import { Download, FileText, LoaderCircle, Plus, Trash2 } from 'lucide-react'
import { useEffect, useRef, useState, type ChangeEvent } from 'react'
import { api } from '../api'
import type { ProjectFile } from '../types'
import './ProjectFormsPanel.css'

interface Props {
  projectId: string
  forms: ProjectFile[]
  onProjectChange: () => Promise<void>
}

const messageOf = (reason: unknown) => reason instanceof Error ? reason.message : 'Operazione non riuscita'

export function ProjectFormsPanel({ projectId, forms, onProjectChange }: Props) {
  const input = useRef<HTMLInputElement>(null)
  const controller = useRef<AbortController | null>(null)
  const working = useRef(false)
  const [busy, setBusy] = useState(false)
  const [progress, setProgress] = useState('')
  const [message, setMessage] = useState('')
  const [errors, setErrors] = useState<string[]>([])
  const [removing, setRemoving] = useState<number | null>(null)

  useEffect(() => {
    controller.current = new AbortController()
    return () => controller.current?.abort()
  }, [])

  function begin() {
    const signal = controller.current?.signal
    if (working.current || !signal || signal.aborted) return null
    working.current = true
    setBusy(true)
    setErrors([])
    setMessage('')
    return signal
  }

  function finish(signal: AbortSignal) {
    working.current = false
    if (!signal.aborted) { setBusy(false); setProgress('') }
  }

  async function upload(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? [])
    event.target.value = ''
    if (!files.length) return
    const signal = begin()
    if (!signal) return
    let uploaded = 0
    const failures: string[] = []
    try {
      for (const [index, file] of files.entries()) {
        if (signal.aborted) return
        setProgress(`Caricamento ${index + 1}/${files.length}: ${file.name}`)
        try {
          if (!/\.(docx|pdf|md|txt)$/i.test(file.name)) throw new Error('Usa DOCX, PDF, TXT o Markdown')
          if (!file.size) throw new Error('Il file e vuoto')
          if (file.size > 20 * 1024 * 1024) throw new Error('Il file supera il limite di 20 MB')
          await api.uploadProjectForm(projectId, file, signal)
          uploaded += 1
        } catch (reason) {
          if (signal.aborted) return
          failures.push(`${file.name}: ${messageOf(reason)}`)
        }
      }
      if (signal.aborted) return
      if (uploaded) {
        setMessage(uploaded === 1 ? '1 modulo caricato.' : `${uploaded} moduli caricati.`)
        try { await onProjectChange() } catch {
          failures.push('File salvati, ma elenco non aggiornato. Ricarica la pagina.')
        }
      }
      if (!signal.aborted) setErrors(failures)
    } finally { finish(signal) }
  }

  async function download(form: ProjectFile) {
    const signal = begin()
    if (!signal) return
    try {
      const blob = await api.downloadProjectForm(projectId, form.id, signal)
      if (signal.aborted) return
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = form.name
      document.body.append(link)
      link.click()
      link.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (reason) {
      if (!signal.aborted) setErrors([messageOf(reason)])
    } finally { finish(signal) }
  }

  async function remove(form: ProjectFile) {
    const signal = begin()
    if (!signal) return
    try {
      await api.deleteProjectForm(projectId, form.id, signal)
      if (signal.aborted) return
      setRemoving(null)
      setMessage(`${form.name} rimosso.`)
      try { await onProjectChange() } catch {
        if (!signal.aborted) setErrors(['Modulo rimosso, ma elenco non aggiornato. Ricarica la pagina.'])
      }
    } catch (reason) {
      if (!signal.aborted) setErrors([messageOf(reason)])
    } finally { finish(signal) }
  }

  return <section className="knowledge-section project-forms" aria-labelledby="project-forms-title">
    <div className="panel-title-row">
      <h2 id="project-forms-title">Moduli da compilare</h2>
      <button className="icon-button" type="button" aria-label="Aggiungi moduli da compilare"
        disabled={busy} onClick={() => input.current?.click()}>
        {busy ? <LoaderCircle size={18} className="spin" /> : <Plus size={18} />}
      </button>
      <input ref={input} type="file" multiple className="source-file-input" disabled={busy}
        aria-label="Seleziona moduli da compilare" accept=".docx,.pdf,.txt,.md" onChange={upload} />
    </div>
    <p className="project-forms-help">DOCX, PDF, TXT o Markdown · Max 20 MB per file</p>
    {progress && <p className="upload-feedback" role="status">{progress}</p>}
    {message && <p className="upload-feedback upload-feedback--success" role="status">{message}</p>}
    {errors.length > 0 && <ul className="project-forms-errors upload-feedback--error" role="alert">
      {errors.map((error, index) => <li key={index}>{error}</li>)}
    </ul>}
    {forms.length === 0 ? <p className="empty-list">Nessun modulo caricato</p> : <ul className="project-forms-list">
      {forms.map((form) => <li key={form.id}>
        <div className="project-form-row">
          <FileText size={17} />
          <div className="project-form-name"><strong title={form.name}>{form.name}</strong><small>{form.metadata}</small></div>
          <button className="icon-button" type="button" disabled={busy}
            title="Scarica originale" aria-label={`Scarica originale ${form.name}`} onClick={() => void download(form)}>
            <Download size={16} />
          </button>
          <button className="icon-button" type="button" disabled={busy}
            title="Rimuovi modulo" aria-label={`Rimuovi ${form.name}`} onClick={() => setRemoving(form.id)}>
            <Trash2 size={16} />
          </button>
        </div>
        {removing === form.id && <div className="project-form-remove">
          <span>Rimuovere questo modulo dal progetto?</span>
          <button type="button" className="button" disabled={busy} onClick={() => setRemoving(null)}>Annulla</button>
          <button type="button" className="button button--danger" disabled={busy} onClick={() => void remove(form)}>Rimuovi modulo</button>
        </div>}
      </li>)}
    </ul>}
  </section>
}
