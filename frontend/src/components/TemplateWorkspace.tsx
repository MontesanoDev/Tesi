import { Download, Eye, FileText, FileUp, NotebookPen, Pencil, Save, WandSparkles } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import Markdown from 'react-markdown'
import remarkFrontmatter from 'remark-frontmatter'
import remarkGfm from 'remark-gfm'
import { api } from '../api'
import type { KnowledgeArtifactDetail } from '../types'
import { LoadingState } from './LoadingState'
import { StatusPill } from './StatusPill'
import { DocxTemplateWorkspace } from './DocxTemplateWorkspace'
import './TemplateWorkspace.css'

type TemplateView = 'model' | 'compilation'

interface Props {
  projectId: string
  template: KnowledgeArtifactDetail
  outputId?: string
  initialView?: TemplateView
  initialFormat?: 'docx' | 'text'
  onUpdated: (artifact: KnowledgeArtifactDetail) => void
  onDirtyChange: (dirty: boolean) => void
}

export function TemplateWorkspace(props: Props) {
  const { onDirtyChange } = props
  const [format, setFormat] = useState(props.initialFormat ?? 'docx')
  const [dirty, setDirty] = useState(false)
  const handleDirty = useCallback((value: boolean) => {
    setDirty(value)
    onDirtyChange(value)
  }, [onDirtyChange])

  return <div className="template-workspace">
    <header className="artifact-editor-heading template-format-heading">
      <h2>Template</h2>
      <label className="template-format">Formato
        <select aria-label="Formato template" value={format} onChange={(event) => {
          if (dirty && !window.confirm('Operazione in corso o modifiche non salvate nel Template. Cambiare formato comunque?')) return
          setFormat(event.target.value as 'docx' | 'text')
        }}>
          <option value="docx">Word (.docx)</option>
          <option value="text">Testo (.md / .txt)</option>
        </select>
      </label>
    </header>
    {format === 'docx'
      ? <DocxTemplateWorkspace key={props.projectId} projectId={props.projectId} onDirtyChange={handleDirty} />
      : <MarkdownTemplateWorkspace {...props} onDirtyChange={handleDirty} />}
  </div>
}

function MarkdownTemplateWorkspace({
  projectId, template, outputId, initialView = 'model', onUpdated, onDirtyChange,
}: Props) {
  const [model, setModel] = useState(template)
  const [modelText, setModelText] = useState(template.content)
  const [output, setOutput] = useState<KnowledgeArtifactDetail | null>(null)
  const [outputText, setOutputText] = useState('')
  const [view, setView] = useState<TemplateView>(initialView)
  const [editing, setEditing] = useState(false)
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)
  const [operation, setOperation] = useState<'save' | 'generate' | 'import' | null>(null)
  const [reload, setReload] = useState(0)
  const fileInput = useRef<HTMLInputElement>(null)
  const active = useRef(false)
  const busy = useRef(false)
  const modelDirty = modelText !== model.content
  const outputDirty = Boolean(output && outputText !== output.content)
  const dirty = modelDirty || outputDirty
  const hasOutput = Boolean(output && output.status !== 'Da generare')
  const hasModel = Boolean(model.content.trim())
  const emptyModel = view === 'model' && !hasModel && !modelDirty && !editing
  const newModelEditor = view === 'model' && !hasModel && editing
  const current = view === 'model' ? model : output
  const text = view === 'model' ? modelText : outputText
  const currentDirty = view === 'model' ? modelDirty : outputDirty
  const editable = Boolean(current?.editable && (view === 'model' || hasOutput))

  useEffect(() => {
    active.current = true
    return () => { active.current = false }
  }, [])

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setLoadError(null)
    if (!outputId) {
      setLoadError('Compilazione non disponibile per questo progetto.')
      setLoading(false)
      return () => controller.abort()
    }
    api.projectArtifact(projectId, outputId, controller.signal)
      .then((item) => {
        if (controller.signal.aborted) return
        setOutput(item)
        setOutputText(item.content)
      })
      .catch((reason) => {
        if (controller.signal.aborted) return
        setLoadError(reason instanceof Error ? reason.message : 'Compilazione non disponibile')
      })
      .finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [projectId, outputId, reload])

  useEffect(() => {
    onDirtyChange(dirty)
    return () => onDirtyChange(false)
  }, [dirty, onDirtyChange])

  useEffect(() => {
    if (!dirty) return
    const beforeUnload = (event: BeforeUnloadEvent) => { event.preventDefault() }
    const beforeLink = (event: MouseEvent) => {
      const link = event.target instanceof Element ? event.target.closest('a') : null
      if (!link || link.target === '_blank' || link.hasAttribute('download')
        || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
      if (!window.confirm('Ci sono modifiche non salvate nel Template. Uscire senza salvarle?')) {
        event.preventDefault()
        event.stopPropagation()
      }
    }
    window.addEventListener('beforeunload', beforeUnload)
    document.addEventListener('click', beforeLink, true)
    return () => {
      window.removeEventListener('beforeunload', beforeUnload)
      document.removeEventListener('click', beforeLink, true)
    }
  }, [dirty])

  async function save() {
    if (!current || !editable || !currentDirty || busy.current || !text.trim()) return
    busy.current = true
    setOperation('save')
    setError(null)
    setMessage(null)
    try {
      const updated = await api.updateProjectArtifact(projectId, current.id, text)
      if (!active.current) return
      if (current.kind === 'template') {
        setModel(updated)
        setModelText(updated.content)
      } else {
        setOutput(updated)
        setOutputText(updated.content)
      }
      onUpdated(updated)
      setMessage(current.kind === 'template' && hasOutput
        ? "Modello salvato. La compilazione precedente non e' stata rigenerata."
        : current.kind === 'template' ? 'Modello salvato.' : 'Compilazione salvata.')
    } catch (reason) {
      if (active.current) setError(reason instanceof Error ? reason.message : 'Salvataggio non riuscito')
    } finally {
      busy.current = false
      if (active.current) setOperation(null)
    }
  }

  async function generate() {
    if (busy.current || dirty || !hasModel || loading || loadError || !model.editable || !output?.editable) return
    if (hasOutput && !window.confirm(
      'Rigenerando perderai la compilazione salvata, incluse le modifiche manuali. Continuare?',
    )) return
    busy.current = true
    setOperation('generate')
    setError(null)
    setMessage(null)
    try {
      const result = await api.generateDraft(projectId)
      if (!active.current) return
      setOutput(result.artifact)
      setOutputText(result.artifact.content)
      onUpdated(result.artifact)
      setView('compilation')
      setEditing(false)
      setMessage(`Compilazione generata: ${result.used_fact_count} di ${result.available_fact_count} dati estratti utilizzati. Dati mancanti: ${result.missing_information.length}.`)
    } catch (reason) {
      if (active.current) setError(reason instanceof Error ? reason.message : 'Generazione non riuscita')
    } finally {
      busy.current = false
      if (active.current) setOperation(null)
    }
  }

  async function importModel(file?: File) {
    if (!file || busy.current || !model.editable) return
    setError(null)
    setMessage(null)
    if (!/\.(md|txt)$/i.test(file.name)) {
      setError('Formato non supportato. Seleziona un modello Markdown (.md) o testo (.txt).')
      return
    }
    if (file.size > 200_000) {
      setError('Il modello supera il limite di 200 KB.')
      return
    }
    if (modelDirty && !window.confirm('Sostituire le modifiche non salvate del modello con il file?')) return
    busy.current = true
    setOperation('import')
    try {
      const imported = new TextDecoder('utf-8', { fatal: true }).decode(await file.arrayBuffer())
      if (!active.current) return
      if (!imported.trim() || imported.includes('\0')) throw new Error('Il file non contiene un modello testuale valido.')
      if ([...imported].length > 50_000) throw new Error('Il modello supera il limite di 50.000 caratteri.')
      setModelText(imported)
      setView('model')
      setEditing(true)
      setMessage(`${file.name} importato. Modifiche non ancora salvate.`)
    } catch (reason) {
      if (active.current) setError(reason instanceof TypeError
        ? 'Impossibile leggere il file come testo UTF-8.'
        : reason instanceof Error ? reason.message : 'Importazione non riuscita')
    } finally {
      busy.current = false
      if (active.current) setOperation(null)
    }
  }

  function download() {
    if (!current || currentDirty || (view === 'compilation' && !hasOutput)) return
    const url = URL.createObjectURL(new Blob([current.content], { type: 'text/markdown;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = view === 'model' ? 'template.md' : 'template-compilato.md'
    link.click()
    window.setTimeout(() => URL.revokeObjectURL(url), 1000)
  }

  return (
    <div className="template-workspace" aria-busy={Boolean(operation)}>
      <div className="template-tabs" role="tablist" aria-label="Template">
        {(['model', 'compilation'] as const).map((tab) => (
          <button key={tab} id={`template-tab-${tab}`} type="button" role="tab"
            aria-selected={view === tab} aria-controls="template-panel"
            tabIndex={view === tab ? 0 : -1} disabled={Boolean(operation)}
            onClick={() => { setView(tab); setEditing(false) }}
            onKeyDown={(event) => {
              if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
              event.preventDefault()
              const next = event.key === 'Home' ? 'model' : event.key === 'End' ? 'compilation'
                : view === 'model' ? 'compilation' : 'model'
              setView(next)
              setEditing(false)
              document.getElementById(`template-tab-${next}`)?.focus()
            }}>
            {tab === 'model' ? 'Modello' : 'Compilazione'}
            {(tab === 'model' ? modelDirty : outputDirty) && <span aria-label="Modifiche non salvate"> *</span>}
          </button>
        ))}
      </div>
      {loadError && <div className="knowledge-error" role="alert">
        {loadError} <button type="button" className="button" onClick={() => setReload((n) => n + 1)}>Riprova</button>
      </div>}
      {error && <div className="knowledge-error" role="alert">{error}</div>}
      <input ref={fileInput} type="file" hidden accept=".md,.txt,text/markdown,text/plain"
        aria-label="Importa modello Markdown o TXT"
        onChange={(event) => {
          const file = event.currentTarget.files?.[0]
          event.currentTarget.value = ''
          void importModel(file)
        }} />
      <section id="template-panel" role="tabpanel" aria-labelledby={`template-tab-${view}`}>
        {!emptyModel && <div className="template-toolbar">
          <span className="template-version">
            {view === 'model' ? hasModel ? `Modello v${model.version}` : 'Nuovo modello' : hasOutput ? `Compilazione v${output?.version}` : 'Nessuna compilazione'}
            {currentDirty ? ' · Modifiche non salvate' : ''}
          </span>
          <div className="template-tools">
            <StatusPill tone={view === 'compilation' && !hasOutput ? 'info' : 'warning'}>
              {view === 'model' ? model.status : hasOutput ? output?.status : 'Da generare'}
            </StatusPill>
            {view === 'model' && <>
              <button type="button" className="button template-import" disabled={Boolean(operation) || !model.editable}
                title="Importa un modello Markdown o TXT" onClick={() => fileInput.current?.click()}>
                <FileUp size={16} /> {hasModel ? 'Cambia modello' : 'Carica modello'}
              </button>
            </>}
            {(view === 'model' || hasOutput) && <>
              <div className="template-display-mode" role="group" aria-label="Visualizzazione documento">
                <button type="button" title="Anteprima" aria-label="Anteprima" aria-pressed={!editing}
                  onClick={() => setEditing(false)}><Eye size={17} /></button>
                <button type="button" title="Modifica testo" aria-label="Modifica testo" aria-pressed={editing}
                  disabled={Boolean(operation) || !editable} onClick={() => setEditing(true)}><Pencil size={17} /></button>
              </div>
              <button type="button" className="template-icon-button" aria-label="Scarica Markdown"
                title={currentDirty ? 'Salva le modifiche prima di scaricare' : 'Scarica Markdown'}
                disabled={Boolean(operation) || currentDirty || (view === 'model' && !hasModel)} onClick={download}><Download size={17} /></button>
            </>}
          </div>
        </div>}
        {emptyModel ? <div className="template-model-empty">
          <FileText size={24} aria-hidden="true" />
          <p>Nessun modello caricato</p>
          <div className="template-model-actions">
            <button className="button button--primary" type="button"
              disabled={Boolean(operation) || !model.editable}
              onClick={() => fileInput.current?.click()}><FileUp size={16} />Carica modello</button>
            <button className="button" type="button" disabled={Boolean(operation) || !model.editable}
              onClick={() => { setEditing(true); setMessage(null); setError(null) }}>
              <NotebookPen size={16} />Crea modello
            </button>
          </div>
        </div> : view === 'compilation' && loading ? <LoadingState label="Caricamento compilazione" />
          : view === 'compilation' && !hasOutput ? <div className="template-empty">
            <FileText size={24} aria-hidden="true" />
            <p>{loadError ? 'Compilazione non disponibile' : 'Nessuna compilazione generata'}</p>
          </div>
          : editing ? <textarea className="markdown-editor template-text-editor"
            autoFocus={newModelEditor}
            aria-label={view === 'model' ? 'Contenuto del modello' : 'Contenuto della compilazione'}
            value={text} readOnly={Boolean(operation) || !editable} spellCheck={false}
            onChange={(event) => {
              if (view === 'model') setModelText(event.target.value)
              else setOutputText(event.target.value)
              setMessage(null)
            }} />
            : <article className="template-preview" aria-label={view === 'model' ? 'Anteprima modello' : 'Anteprima compilazione'}>
              <Markdown remarkPlugins={[remarkFrontmatter, remarkGfm]} skipHtml components={{
                a: ({ href, children }) => <a href={href} target="_blank" rel="noopener noreferrer">{children}</a>,
                img: ({ alt }) => <span>{alt}</span>,
                table: ({ children }) => <div className="template-table"><table>{children}</table></div>,
              }}>{text}</Markdown>
            </article>}
      </section>
      <footer className="template-footer">
        <div className="template-feedback" role="status" aria-live="polite">
          {operation === 'generate' ? 'Generazione in corso...' : message}
        </div>
        <div className="template-footer-actions">
          {(currentDirty || newModelEditor) && <button className="button" type="button" disabled={Boolean(operation)}
            onClick={() => {
              if (currentDirty && !window.confirm('Annullare le modifiche non salvate di questo documento?')) return
              if (view === 'model') {
                setModelText(model.content)
                if (!hasModel) setEditing(false)
              }
              else setOutputText(output?.content ?? '')
              setMessage(null)
            }}>Annulla modifiche</button>}
          {(currentDirty || newModelEditor) && <button className="button button--primary artifact-save" type="button"
            disabled={Boolean(operation) || !editable || !text.trim()} onClick={save}>
            <Save size={16} />{operation === 'save' ? 'Salvataggio' : view === 'model' ? 'Salva modello' : 'Salva compilazione'}
          </button>}
          <button className="button artifact-generate" type="button" disabled={
            Boolean(operation) || loading || Boolean(loadError) || dirty || !hasModel || !model.editable || !output?.editable
          } title={dirty ? 'Salva o annulla le modifiche in Modello e Compilazione prima di generare' : undefined}
            onClick={generate}><WandSparkles size={16} />
            {operation === 'generate' ? 'Generazione in corso' : hasOutput ? 'Rigenera compilazione' : 'Genera compilazione'}
          </button>
        </div>
      </footer>
    </div>
  )
}
