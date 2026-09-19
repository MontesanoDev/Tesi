import { ArrowLeft, ArrowRight, Check, Download, FileText, Printer, RotateCcw, Upload } from 'lucide-react'
import { useRef, useState } from 'react'
import { AppShell } from '../components/AppShell'
import { DEMO_VALUES, EMPTY_VALUES, FIELDS, displayValue, facsimileHtml, fieldIsValid, type FieldKey, type Values } from './candidatureDemo'
import './CandidatureDemoPage.css'

const STEPS = ['Modello', 'Bozza', 'Revisione', 'Esportazione']
interface ModelSelection { name: string; kind: 'example' | 'file' }

export function CandidatureDemoPage() {
  const [step, setStep] = useState(0)
  const [model, setModel] = useState<ModelSelection | null>(null)
  const [values, setValues] = useState<Values>({ ...EMPTY_VALUES })
  const [edited, setEdited] = useState<Partial<Record<FieldKey, boolean>>>({})
  const [generated, setGenerated] = useState(false)
  const [confirmed, setConfirmed] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [downloaded, setDownloaded] = useState(false)
  const fileInput = useRef<HTMLInputElement>(null)
  const missing = FIELDS.filter((field) => !fieldIsValid(field.key, values[field.key]))
  const ready = generated && missing.length === 0 && confirmed

  function chooseModel(selection: ModelSelection) {
    setModel(selection)
    setStep(0)
    setGenerated(false)
    setConfirmed(false)
    setDownloaded(false)
    setValues({ ...EMPTY_VALUES })
    setEdited({})
    setError(null)
  }

  function selectFile(file?: File) {
    if (!file) return
    if (!/\.(pdf|docx)$/i.test(file.name)) {
      setError('Seleziona un modello PDF o DOCX.')
      return
    }
    if (!file.size || file.size > 20 * 1024 * 1024) {
      setError('Seleziona un file non vuoto, fino a 20 MB.')
      return
    }
    // This prototype uses only the filename. File contents never leave the browser.
    chooseModel({ name: file.name, kind: 'file' })
  }

  function generateDemo() {
    if (!model) return
    setValues({ ...DEMO_VALUES })
    setEdited({})
    setGenerated(true)
    setConfirmed(false)
    setDownloaded(false)
    setStep(1)
  }

  function changeField(key: FieldKey, value: string) {
    setValues((current) => ({ ...current, [key]: value }))
    setEdited((current) => ({ ...current, [key]: true }))
    setConfirmed(false)
    setDownloaded(false)
  }

  function reset() {
    setModel(null)
    setStep(0)
    setGenerated(false)
    setConfirmed(false)
    setDownloaded(false)
    setValues({ ...EMPTY_VALUES })
    setEdited({})
    setError(null)
  }

  function download() {
    if (!ready) return
    const url = URL.createObjectURL(new Blob([facsimileHtml(values)], { type: 'text/html;charset=utf-8' }))
    const link = document.createElement('a')
    link.href = url
    link.download = 'facsimile-candidatura-demo.html'
    document.body.append(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1_000)
    setDownloaded(true)
  }

  return (
    <AppShell active="documents" contentClassName="candidature-demo">
      <header className="demo-heading">
        <div><p className="demo-eyebrow">Mapi RAG / proposta di workflow</p><h1>Preparazione candidatura</h1></div>
        <button className="icon-button" title="Ricomincia demo" aria-label="Ricomincia demo" onClick={reset}><RotateCcw size={19} /></button>
      </header>
      <p className="demo-disclosure"><strong>Demo concettuale</strong> Dati fittizi. Nessuna elaborazione dei file, chiamata al modello o modifica ai progetti.</p>

      <nav className="demo-steps" aria-label="Fasi della candidatura">
        {STEPS.map((label, index) => (
          <button
            key={label}
            aria-current={step === index ? 'step' : undefined}
            disabled={index > 0 && !generated || index === 3 && !ready}
            onClick={() => setStep(index)}
          ><span>{index < step ? <Check size={15} /> : index + 1}</span>{label}</button>
        ))}
      </nav>

      <div className="demo-layout">
        <section className="demo-controls" aria-label={STEPS[step]}>
          <span className="demo-eyebrow">Passaggio {step + 1} di 4</span>
          <h2>{['Modello da compilare', 'Bozza proposta', 'Revisione dei dati', 'Documento da scaricare'][step]}</h2>

          {step === 0 && <>
            <div className="demo-upload" onDragOver={(event) => event.preventDefault()} onDrop={(event) => {
              event.preventDefault()
              selectFile(event.dataTransfer.files[0])
            }}>
              <FileText size={28} />
              <strong>{model?.name ?? 'Modello della candidatura'}</strong>
              <span>{model ? 'Selezionato per la simulazione' : 'PDF o DOCX / fino a 20 MB'}</span>
              <button className="button" onClick={() => fileInput.current?.click()}><Upload size={16} />{model ? 'Sostituisci modello' : 'Carica modello'}</button>
              <input ref={fileInput} type="file" accept=".pdf,.docx" aria-label="Seleziona modello dimostrativo" hidden onChange={(event) => {
                selectFile(event.currentTarget.files?.[0])
                event.currentTarget.value = ''
              }} />
            </div>
            {error && <p role="alert" className="demo-error">{error}</p>}
            <button className="demo-example" onClick={() => chooseModel({ name: 'Modello candidatura - esempio', kind: 'example' })}>Usa modello dimostrativo</button>
            {model?.kind === 'file' && <p className="demo-file-notice">Il file non viene letto o conservato. A destra resta il facsimile della demo, non il documento selezionato.</p>}
            <div className="demo-source-list">
              <h3>Fonti della simulazione</h3>
              <p><FileText size={16} /><span>Scheda progetto<small>Ente e intervento fittizi</small></span></p>
              <p><FileText size={16} /><span>Company KB<small>Supporto tecnico dimostrativo</small></span></p>
            </div>
            <button className="button button--primary demo-next" disabled={!model} onClick={generateDemo}>Simula compilazione<ArrowRight size={17} /></button>
          </>}

          {step === 1 && <>
            <div className="demo-counts"><p><strong>{FIELDS.length - missing.length}</strong>campi compilati</p><p><strong>{missing.length}</strong>da completare</p></div>
            <p className="demo-file-notice">Valori di esempio, non estratti dal modello selezionato.</p>
            <h3>Dati da completare</h3>
            {missing.length ? <ul className="demo-missing-list">{missing.map((field) => <li key={field.key}>{field.label}</li>)}</ul> : <p className="demo-success">Tutti i campi sono compilati.</p>}
            <button className="button button--primary demo-next" onClick={() => setStep(2)}>Revisiona bozza<ArrowRight size={17} /></button>
          </>}

          {step === 2 && <>
            <p className="demo-review-status" role="status">{missing.length ? `${missing.length} dati da completare` : 'Tutti i campi sono compilati'}</p>
            <div className="demo-fields">
              {FIELDS.map((field) => (
                <label key={field.key}>
                  <span id={`demo-label-${field.key}`}>{field.label}</span>
                  <input
                    aria-labelledby={`demo-label-${field.key}`}
                    aria-describedby={`demo-source-${field.key}`}
                    required
                    type={field.key === 'importo' ? 'number' : 'text'}
                    min={field.key === 'importo' ? '0.01' : undefined}
                    step={field.key === 'importo' ? '0.01' : undefined}
                    maxLength={field.key === 'importo' ? undefined : 400}
                    value={values[field.key]}
                    onChange={(event) => changeField(field.key, event.currentTarget.value)}
                    aria-invalid={!fieldIsValid(field.key, values[field.key])}
                  />
                  <small id={`demo-source-${field.key}`}>{edited[field.key] ? 'Inserito in revisione' : field.source ? `${field.source} / demo` : 'Non disponibile nelle fonti simulate'}</small>
                </label>
              ))}
            </div>
            <label className="demo-confirm"><input type="checkbox" checked={confirmed} onChange={(event) => setConfirmed(event.currentTarget.checked)} />Ho controllato i dati del facsimile</label>
            <button className="button button--primary demo-next" disabled={!ready} onClick={() => setStep(3)}>Vai all'esportazione<ArrowRight size={17} /></button>
          </>}

          {step === 3 && <>
            <p className="demo-ready"><Check size={18} />Facsimile revisionato</p>
            <p className="demo-file-notice">Il download contiene questo facsimile HTML, non il PDF o DOCX caricato. La compilazione del modello originale resta da implementare.</p>
            <button className="button button--primary demo-next" disabled={!ready} onClick={download}><Download size={17} />Scarica facsimile HTML</button>
            <button className="button demo-next" disabled={!ready} onClick={() => window.print()}><Printer size={17} />Stampa / PDF</button>
            {downloaded && <p role="status" className="demo-success">Download del facsimile avviato.</p>}
          </>}
          {step > 0 && <button className="demo-back" onClick={() => setStep(step - 1)}><ArrowLeft size={15} />Indietro</button>}
        </section>

        <section className="demo-preview" aria-label="Anteprima del facsimile">
          <div className="demo-preview-heading"><span><FileText size={16} />Facsimile dimostrativo</span><span>Formato A4</span></div>
          <article className="demo-paper">
            <header><strong>FACSIMILE / DATI DIMOSTRATIVI</strong><span>Allegato A</span></header>
            <h2>Istanza di candidatura</h2>
            <p className="demo-paper-subtitle">Interventi di riqualificazione dell'edilizia scolastica</p>
            <dl>{FIELDS.map((field, index) => (
              <div className={!fieldIsValid(field.key, values[field.key]) ? 'demo-paper-missing' : ''} key={field.key}>
                <dt><span>{String(index + 1).padStart(2, '0')}</span>{field.label}</dt>
                <dd>{fieldIsValid(field.key, values[field.key]) ? displayValue(field.key, values[field.key]) : generated ? 'Da completare' : '[ Campo da compilare ]'}</dd>
              </div>
            ))}</dl>
            <footer>Simulazione del flusso di Mapi RAG.<br />Documento dimostrativo, non utilizzabile per invii ufficiali.</footer>
          </article>
        </section>
      </div>
    </AppShell>
  )
}
