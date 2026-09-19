import { Download, FileText, FileUp, LoaderCircle, RotateCcw, WandSparkles, X } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'
import { api } from '../api'
import type { CompilationDownload, CompilationField, DocumentCompilation, DocumentCompilationSummary } from '../types'
import { LoadingState } from './LoadingState'
import { StatusPill } from './StatusPill'
import './DocxTemplateWorkspace.css'

interface Props {
  projectId: string
  onDirtyChange: (dirty: boolean) => void
}

const DOCX_MIME = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
const dateLabel = (date: string) => new Date(date).toLocaleString('it-IT', { dateStyle: 'short', timeStyle: 'short' })
const messageOf = (error: unknown) => error instanceof Error ? error.message : 'Operazione non riuscita'
const unresolved = (field: CompilationField) => field.written_value === null && field.status !== 'not_applicable'
type WorkspaceView = 'new' | 'saved'

function FieldRow({ field }: { field: CompilationField }) {
  const inserted = field.written_value !== null
  const status = inserted ? 'Inserito' : field.validation_notes.length > 0 ? 'Bloccato'
    : field.status === 'missing' ? 'Mancante'
    : field.status === 'not_applicable' ? 'Non applicabile' : 'Da verificare'
  return <li className="docx-field">
    <details>
      <summary>
        <span className="docx-field-data"><strong>{field.label}</strong>
          <span>{field.written_value ?? 'Non compilato'}</span>
        </span>
        <StatusPill tone={inserted ? 'success' : field.status === 'not_applicable' ? 'info' : 'warning'}>{status}</StatusPill>
      </summary>
      <div className="docx-field-detail">
        <p>{field.reason}</p>
        {!inserted && field.value && <p><strong>Proposta non inserita:</strong> {field.value}</p>}
        {field.validation_notes.length > 0 && <ul>{field.validation_notes.map((note, i) => <li key={i}>{note}</li>)}</ul>}
        {field.rejected_evidence && field.rejected_evidence.length > 0 && <>
          <strong>Riferimenti rifiutati</strong>
          <ul>{field.rejected_evidence.map((source, i) => <li key={i}>
            {source.source_id}: {source.quote} ({source.reason})
          </li>)}</ul>
        </>}
        {field.repair && <>
          <strong>{field.repair.status === 'corrected' ? 'Correzione automatica applicata' : 'Correzione non applicata'}</strong>
          <p>{field.repair.message}</p>
          {field.repair.initial_proposal.value && <p>Proposta iniziale: {field.repair.initial_proposal.value}</p>}
          <ul>{field.repair.initial_proposal.validation_notes.map((note, i) => <li key={i}>Controllo iniziale: {note}</li>)}</ul>
        </>}
        {field.evidence.map((source, i) => <blockquote key={`${source.source_id}:${i}`}>
          <p>{source.quote}</p>
          <cite>{source.source_name}
            {source.origin === 'user' && " · Dato dichiarato dall'utente"}
            {source.origin === 'extracted' && ' · Sintesi automatica'}
            {source.fragment !== null && ` · Frammento ${source.fragment}`}
            {source.page !== null && ` · Pagina ${source.page}`}
          </cite>
        </blockquote>)}
        <small>{field.location?.kind === 'paragraph'
          ? `Paragrafo ${field.location.paragraph} · Campo ${field.location.slot} · ${field.cell_id}`
          : `Cella ${field.cell_id}`}</small>
      </div>
    </details>
  </li>
}

export function DocxTemplateWorkspace({ projectId, onDirtyChange }: Props) {
  const [view, setView] = useState<WorkspaceView>('new')
  const [file, setFile] = useState<File | null>(null)
  const [instructions, setInstructions] = useState('')
  const [runs, setRuns] = useState<DocumentCompilationSummary[]>([])
  const [selectedId, setSelectedId] = useState('')
  const [run, setRun] = useState<DocumentCompilation | null>(null)
  const [loading, setLoading] = useState(true)
  const [detailLoading, setDetailLoading] = useState(false)
  const [listError, setListError] = useState<string | null>(null)
  const [detailError, setDetailError] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [downloadError, setDownloadError] = useState<string | null>(null)
  const [generating, setGenerating] = useState(false)
  const [download, setDownload] = useState<CompilationDownload | 'reuse' | null>(null)
  const [reload, setReload] = useState(0)
  const [detailReload, setDetailReload] = useState(0)
  const [filter, setFilter] = useState('all')
  const input = useRef<HTMLInputElement>(null)
  const active = useRef(false)
  const busy = useRef(false)
  const createdRun = useRef<DocumentCompilation | null>(null)
  const dirty = Boolean(file || instructions.trim() || generating)

  useEffect(() => {
    active.current = true
    return () => { active.current = false }
  }, [])

  useEffect(() => {
    onDirtyChange(dirty)
    return () => onDirtyChange(false)
  }, [dirty, onDirtyChange])

  useEffect(() => {
    if (!dirty) return
    const beforeUnload = (event: BeforeUnloadEvent) => event.preventDefault()
    const beforeLink = (event: MouseEvent) => {
      const link = event.target instanceof Element ? event.target.closest('a') : null
      if (!link || link.target === '_blank' || link.hasAttribute('download')
        || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return
      if (!window.confirm('Operazione in corso o modello non ancora compilato. Uscire dal Template?')) {
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

  useEffect(() => {
    const controller = new AbortController()
    setLoading(true)
    setListError(null)
    api.documentCompilations(projectId, controller.signal).then((items) => {
      if (controller.signal.aborted) return
      setRuns(items)
    }).catch((reason) => {
      if (!controller.signal.aborted) setListError(messageOf(reason))
    }).finally(() => { if (!controller.signal.aborted) setLoading(false) })
    return () => controller.abort()
  }, [projectId, reload])

  useEffect(() => {
    if (view === 'saved' && !loading && runs.length && !runs.some((item) => item.id === selectedId)) {
      setSelectedId(runs[0].id)
    }
  }, [view, loading, runs, selectedId])

  useEffect(() => {
    const controller = new AbortController()
    setRun(null)
    setDetailError(null)
    setDownloadError(null)
    setFilter('all')
    if (view !== 'saved' || !selectedId || createdRun.current?.id === selectedId) {
      setRun(view === 'saved' && selectedId ? createdRun.current : null)
      setDetailLoading(false)
      return () => controller.abort()
    }
    setDetailLoading(true)
    api.documentCompilation(projectId, selectedId, controller.signal).then((result) => {
      if (!controller.signal.aborted) setRun(result)
    }).catch((reason) => {
      if (!controller.signal.aborted) setDetailError(messageOf(reason))
    }).finally(() => { if (!controller.signal.aborted) setDetailLoading(false) })
    return () => controller.abort()
  }, [projectId, selectedId, detailReload, view])

  function changeView(next: WorkspaceView) {
    if (busy.current || loading) return
    if (next === 'saved' && !selectedId) setSelectedId(runs[0]?.id ?? '')
    setView(next)
  }

  function resetCompilation() {
    if (busy.current) return
    if (dirty && !window.confirm('Scartare il modello selezionato e le indicazioni? Le compilazioni salvate restano disponibili.')) return
    setFile(null)
    setInstructions('')
    setError(null)
    setDownloadError(null)
    setDetailError(null)
    setSelectedId('')
    setRun(null)
    setFilter('all')
    createdRun.current = null
    if (input.current) input.current.value = ''
    setView('new')
  }

  function chooseFile(candidate?: File) {
    if (!candidate || busy.current) return
    setError(null)
    if (!/\.docx$/i.test(candidate.name)) {
      setError('Formato non supportato: serve un modello Word .docx. PDF e .doc non sono ancora supportati.')
      return
    }
    if (!candidate.size || candidate.size > 20 * 1024 * 1024) {
      setError(candidate.size ? 'Il modello supera il limite di 20 MB.' : 'Il file selezionato e vuoto.')
      return
    }
    if (candidate.name.length > 180 || [...candidate.name].some((character) => character.charCodeAt(0) < 32)) {
      setError('Nome del modello non valido: massimo 180 caratteri, senza caratteri di controllo.')
      return
    }
    setFile(candidate)
  }

  async function generate() {
    if (!file || busy.current || loading || detailLoading) return
    busy.current = true
    setGenerating(true)
    setError(null)
    try {
      const result = await api.compileDocument(projectId, file, instructions.trim())
      if (!active.current) return
      createdRun.current = result
      setRuns((items) => [result, ...items.filter((item) => item.id !== result.id)].slice(0, 100))
      setSelectedId(result.id)
      setFile(null)
      setInstructions('')
      setView('saved')
    } catch (reason) {
      if (active.current) setError(messageOf(reason))
    } finally {
      busy.current = false
      if (active.current) setGenerating(false)
    }
  }

  async function getFile(kind: CompilationDownload | 'reuse') {
    if (!run || busy.current) return
    if (kind === 'reuse' && dirty && !window.confirm('Sostituire il modello selezionato e le indicazioni con quelli di questa compilazione?')) return
    busy.current = true
    setDownload(kind)
    setDownloadError(null)
    try {
      const blob = await api.downloadCompilation(projectId, run.id, kind === 'reuse' ? 'template' : kind)
      if (!active.current) return
      if (kind === 'reuse') {
        setFile(new File([blob], run.template_name, { type: DOCX_MIME }))
        setInstructions(run.report.instructions)
        setError(null)
        setView('new')
      } else {
        const url = URL.createObjectURL(blob)
        const link = document.createElement('a')
        link.href = url
        link.download = kind === 'docx' ? run.template_name.replace(/\.docx$/i, '-bozza.docx')
          : kind === 'report' ? 'report.json' : run.template_name
        link.click()
        window.setTimeout(() => URL.revokeObjectURL(url), 1000)
      }
    } catch (reason) {
      if (active.current) setDownloadError(messageOf(reason))
    } finally {
      busy.current = false
      if (active.current) setDownload(null)
    }
  }

  const disabled = generating || download !== null
  const fields = run?.report.fields.filter((field) => filter === 'all'
    || (filter === 'unresolved' ? unresolved(field) : field.written_value !== null)) ?? []
  const unclassified = run?.report.unclassified_fields ?? run?.report.unclassified_cells ?? []
  const modelNames = [...new Set(runs.map((item) => item.template_name))]

  return <div className="docx-workspace" aria-busy={generating}>
    <div className="template-tabs docx-tabs" role="tablist" aria-label="Compilazione Word">
      {(['new', 'saved'] as const).map((tab) => <button key={tab} id={`docx-tab-${tab}`}
        type="button" role="tab" aria-selected={view === tab} aria-controls={`docx-panel-${tab}`}
        tabIndex={view === tab ? 0 : -1} disabled={disabled || loading}
        onClick={() => changeView(tab)} onKeyDown={(event) => {
          if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return
          event.preventDefault()
          const next = event.key === 'Home' ? 'new' : event.key === 'End' ? 'saved'
            : view === 'new' ? 'saved' : 'new'
          changeView(next)
          document.getElementById(`docx-tab-${next}`)?.focus()
        }}>
        {tab === 'new' ? 'Nuova compilazione' : `Compilazioni salvate (${runs.length})`}
        {tab === 'new' && dirty && <span aria-label="Modello non ancora compilato"> *</span>}
      </button>)}
    </div>
    {listError && <div className="knowledge-error" role="alert">{listError} <button className="button" type="button"
      disabled={disabled} onClick={() => setReload((value) => value + 1)}>Ricarica compilazioni</button></div>}
    {view === 'new' && <section id="docx-panel-new" role="tabpanel" aria-labelledby="docx-tab-new">
    {error && <div className="knowledge-error" role="alert">{error}</div>}
    <form className="docx-form" onSubmit={(event) => { event.preventDefault(); void generate() }}>
      <div className="docx-model-row">
        <FileText size={23} aria-hidden="true" />
        <div className="docx-model-name"><strong>{file?.name ?? 'Modello Word da compilare'}</strong>
          <small>{file ? `${Math.max(1, Math.ceil(file.size / 1024))} KB · Non ancora compilato` : 'DOCX con celle vuote o segnaposti · Max 20 MB'}</small>
        </div>
        <input ref={input} type="file" hidden accept={`.docx,${DOCX_MIME}`} aria-label="Carica modello DOCX"
          disabled={disabled} onChange={(event) => {
            chooseFile(event.currentTarget.files?.[0])
            event.currentTarget.value = ''
          }} />
        <button type="button" className="button" disabled={disabled} onClick={() => input.current?.click()}>
          <FileUp size={16} />{file ? 'Cambia modello' : 'Carica modello'}
        </button>
        {file && <button type="button" className="template-icon-button" title="Rimuovi modello selezionato"
          aria-label="Rimuovi modello selezionato" disabled={disabled} onClick={() => { setFile(null); setError(null) }}><X size={17} /></button>}
      </div>
      <label className="docx-instructions" htmlFor="docx-instructions">Indicazioni per la compilazione <span>Facoltative</span></label>
      <textarea id="docx-instructions" rows={3} maxLength={4000} value={instructions}
        disabled={disabled} onChange={(event) => setInstructions(event.target.value)} />
      <div className="docx-form-footer">
        <span>{instructions.length} / 4000</span>
        <div className="docx-form-actions">
        <button type="button" className="template-icon-button" title="Reimposta compilazione"
          aria-label="Reimposta compilazione" disabled={disabled || (!dirty && !error)} onClick={resetCompilation}>
          <RotateCcw size={17} />
        </button>
        <button className="button button--primary" type="submit" disabled={disabled || !file || loading || detailLoading}>
          {generating ? <LoaderCircle size={16} className="docx-spinner" /> : <WandSparkles size={16} />}
          {generating ? 'Compilazione in corso' : 'Compila Word'}
        </button>
        </div>
      </div>
      {generating && <p className="docx-progress" role="status">Analisi del modello e delle fonti in corso. La compilazione puo richiedere alcuni minuti.</p>}
    </form>
    </section>}
    {view === 'saved' && <section id="docx-panel-saved" role="tabpanel" aria-labelledby="docx-tab-saved">
    {loading ? <LoadingState label="Caricamento compilazioni Word" /> : runs.length === 0 && !listError
      ? <p className="docx-no-runs">Nessuna compilazione Word salvata.</p> : null}
    {runs.length > 0 && <section className="docx-results" aria-label="Compilazioni Word">
      <div className="docx-history">
        <label htmlFor="docx-history">Compilazioni salvate</label>
        <select id="docx-history" value={selectedId} disabled={disabled || loading}
          onChange={(event) => setSelectedId(event.target.value)}>
          {modelNames.map((name) => <optgroup key={name} label={name}>
            {runs.filter((item) => item.template_name === name).map((item) =>
              <option key={item.id} value={item.id}>{item.template_name} · {dateLabel(item.created_at)} · {item.id.slice(0, 6)}</option>)}
          </optgroup>)}
        </select>
      </div>
      {downloadError && <div className="knowledge-error" role="alert">{downloadError}</div>}
      {detailError && <div className="knowledge-error" role="alert">{detailError} <button className="button" type="button"
        disabled={disabled} onClick={() => setDetailReload((value) => value + 1)}>Riprova</button></div>}
      {detailLoading ? <LoadingState label="Caricamento report" /> : run && <>
        <div className="docx-result-heading"><div><h3>{run.template_name}</h3><small>{dateLabel(run.created_at)}</small></div>
          <StatusPill tone="warning">Da verificare</StatusPill>
        </div>
        <p className="docx-review-notice">Bozza non verificata. Nessuna firma o invio eseguiti.</p>
        <div className="docx-downloads">
          <button type="button" className="button button--primary" disabled={disabled} onClick={() => void getFile('docx')}>
            <Download size={16} />Scarica Word compilato
          </button>
          <button type="button" className="button" disabled={disabled} onClick={() => void getFile('report')}><Download size={16} />Report JSON</button>
          <button type="button" className="button" disabled={disabled} onClick={() => void getFile('template')}><Download size={16} />Modello originale</button>
          <button type="button" className="button" disabled={disabled} onClick={() => void getFile('reuse')}><RotateCcw size={16} />Riutilizza modello</button>
        </div>
        {download && <p role="status" className="docx-progress">{download === 'reuse' ? 'Caricamento modello...' : 'Download in corso...'}</p>}
        <dl className="docx-counts">
          <div><dt>Campi inseriti</dt><dd>{run.report.written_field_count}</dd></div>
          <div><dt>Da completare / verificare</dt><dd>{run.report.unresolved_field_count}</dd></div>
          <div><dt>Elementi non classificati</dt><dd>{unclassified.length}</dd></div>
        </dl>
        <details className="docx-warnings">
          <summary>Avvisi e copertura fonti ({run.report.warnings.length})</summary>
          <p>{run.report.source_coverage.selected_chunks} / {run.report.source_coverage.total_chunks} frammenti utilizzati
            {run.report.source_coverage.partial ? ' · Contesto parziale' : ''}</p>
          <ul>{run.report.warnings.map((warning, i) => <li key={i}>{warning}</li>)}</ul>
          {unclassified.length > 0 && <p>Elementi non classificati, non necessariamente campi mancanti: {unclassified.join(', ')}</p>}
          {Boolean(run.report.unsupported_locations?.length) && <>
            <h4>Parti non supportate</h4>
            <ul>{run.report.unsupported_locations?.map((location) => <li key={location.paragraph}>
              Paragrafo {location.paragraph}: {location.reason}
            </li>)}</ul>
          </>}
          {run.report.instructions && <><h4>Indicazioni utilizzate</h4><p className="docx-saved-instructions">{run.report.instructions}</p></>}
        </details>
        <div className="docx-fields-heading"><h3>Campi del documento</h3>
          <select aria-label="Filtra campi" value={filter} onChange={(event) => setFilter(event.target.value)}>
            <option value="all">Tutti ({run.report.fields.length})</option>
            <option value="unresolved">Da completare / verificare</option>
            <option value="written">Inseriti</option>
          </select>
        </div>
        <ul className="docx-fields">{fields.map((field) => <FieldRow key={`${run.id}:${field.cell_id}`} field={field} />)}</ul>
        {fields.length === 0 && <p className="docx-no-runs">Nessun campo in questa vista.</p>}
      </>}
    </section>}
    </section>}
  </div>
}
