import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { EmbeddingProvider, EmbeddingProviderDefinition, RetrievalInput, RetrievalSettings } from '../types'
import { ServiceAddressFields } from './ServiceAddressFields'
import './AiSettings.css'
import './RetrievalSettings.css'

function formValue(settings: RetrievalSettings): RetrievalInput {
  const { has_qdrant_api_key: _q, has_embedding_api_key: _e, ...config } = settings
  return { ...config, embedding_provider: config.embedding_provider ?? 'ollama', qdrant_api_key: '', embedding_api_key: '',
    clear_qdrant_api_key: false, clear_embedding_api_key: false }
}

function sameModel(left: string, right: string) {
  return left.replace(/:latest$/, '') === right.replace(/:latest$/, '')
}

function indexConfigDiffers(next: RetrievalInput, previous: RetrievalSettings) {
  return next.embedding_provider !== (previous.embedding_provider ?? 'ollama') ||
    next.embedding_model !== previous.embedding_model || next.embedding_url !== previous.embedding_url ||
    next.qdrant_mode !== previous.qdrant_mode ||
    (next.qdrant_mode === 'remote' && next.qdrant_url !== previous.qdrant_url)
}

// The embedding service an inventory belongs to: a different key or address needs a new inventory.
function serviceKey(config: RetrievalInput) {
  return JSON.stringify([config.embedding_provider, config.embedding_url, config.embedding_api_key, config.clear_embedding_api_key])
}

type SaveState = { kind: 'idle' | 'saving' | 'saved' | 'incomplete' | 'error'; message?: string }

export function RetrievalSettingsPanel() {
  const [saved, setSaved] = useState<RetrievalSettings | null>(null)
  const [providers, setProviders] = useState<EmbeddingProviderDefinition[]>([])
  const [form, setForm] = useState<RetrievalInput | null>(null)
  const [busy, setBusy] = useState<'check' | 'index' | ''>('')
  const [saveState, setSaveState] = useState<SaveState>({ kind: 'idle' })
  const [commitRequest, setCommitRequest] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState('')
  const [attempt, setAttempt] = useState(0)
  const [searchOpen, setSearchOpen] = useState(false)
  const [embeddingOpen, setEmbeddingOpen] = useState(false)
  const [models, setModels] = useState<string[] | null>(null)
  const [modelsLoading, setModelsLoading] = useState(false)
  const [modelsError, setModelsError] = useState('')
  const [connection, setConnection] = useState<{ kind: 'checking' | 'success' | 'warning' | 'error'; message: string } | null>(null)
  const modelsRequest = useRef<AbortController | null>(null)
  const modelsService = useRef('')
  const formRef = useRef<HTMLFormElement>(null)
  const saving = useRef(false)
  const saveAgain = useRef(false)
  const embeddingServiceRef = useRef<HTMLDivElement>(null)

  async function loadModels(config: RetrievalInput, verify = false) {
    modelsRequest.current?.abort()
    const controller = new AbortController()
    modelsRequest.current = controller
    modelsService.current = serviceKey(config)
    setModels(null)
    setModelsLoading(true)
    setModelsError('')
    setConnection(verify ? { kind: 'checking', message: 'Verifica del collegamento in corso…' } : null)
    try {
      const result = await api.embeddingModels({
        embedding_provider: config.embedding_provider,
        embedding_url: config.embedding_url, embedding_api_key: config.embedding_api_key,
        clear_embedding_api_key: config.clear_embedding_api_key,
      }, controller.signal)
      if (!controller.signal.aborted) {
        setModels(result.models)
        if (verify) {
          const listed = result.models.some((model) => config.embedding_provider === 'ollama'
            ? sameModel(model, config.embedding_model) : model === config.embedding_model)
          setConnection(listed
            ? { kind: 'success', message: `Collegamento riuscito. Il modello ${config.embedding_model} è disponibile nell’elenco.` }
            : { kind: 'warning', message: 'Servizio raggiungibile. Il modello selezionato non compare nell’elenco: la sua disponibilità resta da verificare.' })
        }
      }
    } catch (reason) {
      if (!controller.signal.aborted) {
        const message = reason instanceof Error ? reason.message : 'Modelli non disponibili'
        if (verify) setConnection({ kind: 'error', message: `Verifica non riuscita: ${message}` })
        else setModelsError(message)
      }
    } finally {
      if (!controller.signal.aborted) setModelsLoading(false)
    }
  }

  useEffect(() => {
    const controller = new AbortController()
    Promise.all([api.retrievalSettings(controller.signal), api.embeddingProviders(controller.signal)]).then(([settings, availableProviders]) => {
      if (controller.signal.aborted) return
      setSaved(settings)
      setProviders(availableProviders)
      setForm(formValue(settings))
      setError(null)
      void loadModels(formValue(settings))
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Ricerca non disponibile')
    })
    return () => { controller.abort(); modelsRequest.current?.abort() }
  }, [attempt])

  const dirty = !!saved && JSON.stringify(form) !== JSON.stringify(formValue(saved))
  const semantic = form?.backend === 'qdrant'
  const provider = providers.find((item) => item.id === form?.embedding_provider)
  const sameEmbeddingService = saved && form && (saved.embedding_provider ?? 'ollama') === form.embedding_provider && saved.embedding_url === form.embedding_url
  // A saved key is never sent to a changed address: the backend rejects the save until it is replaced or removed.
  const embeddingKeyPending = !!saved?.has_embedding_api_key && !sameEmbeddingService &&
    !form?.clear_embedding_api_key && !form?.embedding_api_key?.trim()
  const qdrantKeyPending = !!saved?.has_qdrant_api_key && !!form && form.qdrant_url !== saved.qdrant_url &&
    !form.clear_qdrant_api_key && !form.qdrant_api_key?.trim()
  const modelOptions = [...new Set((models ?? []).map((name) =>
    form && (name === form.embedding_model || form.embedding_provider === 'ollama' && sameModel(name, form.embedding_model))
      ? form.embedding_model : name))]

  function change(patch: Partial<RetrievalInput>) {
    setConnection(null)
    if ('embedding_provider' in patch || 'embedding_url' in patch || 'embedding_api_key' in patch || 'clear_embedding_api_key' in patch) {
      modelsRequest.current?.abort()
      modelsService.current = ''
      setModels(null); setModelsLoading(false); setModelsError('')
    }
    setForm((value) => value ? { ...value, ...patch } : value)
    setNotice('')
    setError(null)
    setSaveState((state) => state.kind === 'saving' ? state : { kind: 'idle' })
  }

  function requestCommit() {
    setCommitRequest((value) => value + 1)
  }

  // Selects and checkboxes commit at once, text fields on leaving the field or on Enter, so
  // half-typed addresses and keys are never stored. Runs after render to read current validity.
  async function autosave() {
    if (!form || !saved) return
    if (!dirty) {
      setSaveState((state) => state.kind === 'incomplete' ? { kind: 'idle' } : state)
      return
    }
    if (saving.current) { saveAgain.current = true; return }
    if (embeddingKeyPending || qdrantKeyPending || !formRef.current?.checkValidity()) {
      setSaveState({ kind: 'incomplete' })
      return
    }
    const snapshot = form
    const previous = saved
    saving.current = true
    setSaveState({ kind: 'saving' })
    try {
      const settings = await api.saveRetrievalSettings(snapshot)
      setSaved(settings)
      // Edits made while the request was in flight stay in the form and are saved next.
      setForm((current) => JSON.stringify(current) === JSON.stringify(snapshot) ? formValue(settings) : current)
      // Reload only a stale inventory: a check already running for this service must not be cancelled.
      if (serviceKey(formValue(settings)) !== modelsService.current) void loadModels(formValue(settings))
      setSaveState({ kind: 'saved', message: settings.backend !== 'qdrant'
        ? 'Impostazioni salvate. La ricerca usa le parole chiave.'
        : indexConfigDiffers(snapshot, previous)
          ? 'Impostazioni salvate. L’indice si aggiornerà alla prossima ricerca semantica, oppure con «Aggiorna indice».'
          : 'Impostazioni salvate.' })
    } catch (reason) {
      setSaveState({ kind: 'error', message: `Salvataggio non riuscito: ${reason instanceof Error ? reason.message : 'riprova.'}` })
    } finally {
      saving.current = false
      if (saveAgain.current) { saveAgain.current = false; requestCommit() }
    }
  }

  useEffect(() => {
    if (commitRequest) void autosave()
    // eslint-disable-next-line react-hooks/exhaustive-deps -- each request saves the form of its own render
  }, [commitRequest])

  function validEmbeddingService() {
    const inputs = embeddingServiceRef.current?.querySelectorAll('input')
    if (!inputs) return false
    for (const input of inputs) {
      if (!input.reportValidity()) { setEmbeddingOpen(true); return false }
    }
    return true
  }

  function changeProvider(id: EmbeddingProvider) {
    const selected = providers.find((item) => item.id === id)
    if (!selected || id === form?.embedding_provider) return
    change({ embedding_provider: id, embedding_url: selected.base_url,
      embedding_model: selected.default_model, embedding_api_key: '',
      clear_embedding_api_key: !!saved?.has_embedding_api_key })
    setEmbeddingOpen(true)
  }

  async function perform(action: 'check' | 'index') {
    if (!form || busy) return
    if (action === 'check' && !formRef.current?.reportValidity()) return
    if (action === 'index' && (dirty || saving.current || !semantic || saved?.backend !== 'qdrant')) return
    setBusy(action)
    setError(null)
    setNotice('')
    try {
      if (action === 'check') {
        const result = await api.checkRetrievalConnection(form)
        setNotice(result.message)
      } else {
        const result = await api.updateVectorIndex()
        setNotice(`Indice aggiornato: ${result.indexed_chunks} frammenti, ${result.updated_chunks} aggiornati e ${result.deleted_chunks} rimossi.`)
      }
    } catch (reason) {
      const context = { check: 'Verifica non riuscita', index: 'Aggiornamento indice non riuscito' }
      setError(`${context[action]}: ${reason instanceof Error ? reason.message : 'riprova.'}`)
    } finally {
      setBusy('')
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    requestCommit()
  }

  return <div className="retrieval-settings">
    {!form && <section className="settings-card ai-settings" aria-labelledby="retrieval-heading">
      <h2 id="retrieval-heading">Ricerca nelle fonti</h2>
      {!error ? <p role="status">Caricamento impostazioni di ricerca…</p>
        : <div className="ai-error" role="alert">{error}<button className="ai-button" onClick={() => {
          setError(null); setAttempt((value) => value + 1)
        }}>Riprova</button></div>}
    </section>}
    {form && <form ref={formRef} className="ai-profile-form retrieval-form" onSubmit={submit}
      onChange={(event) => {
        const target = event.target
        if (target instanceof HTMLSelectElement || target instanceof HTMLInputElement && target.type === 'checkbox') requestCommit()
      }}
      onBlur={requestCommit}
      onInvalidCapture={(event) => {
        const details = event.target instanceof Element ? event.target.closest('details') : null
        if (!details) return
        if (embeddingServiceRef.current && details.contains(embeddingServiceRef.current)) setEmbeddingOpen(true)
        else setSearchOpen(true)
      }} aria-busy={!!busy}>
      <fieldset disabled={!!busy}>
        <section className="settings-card ai-settings retrieval-card" aria-labelledby="embedding-heading">
          <h2 id="embedding-heading">Modelli di embedding</h2>
          <label>Provider di embedding
            <select value={form.embedding_provider} onChange={(e) => changeProvider(e.target.value as EmbeddingProvider)}>
              {providers.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
            </select>
          </label>
          <label>Modello di embedding
            {form.embedding_provider === 'compatible'
              ? <input type="text" required maxLength={160} value={form.embedding_model} list="embedding-available-models"
                onChange={(e) => change({ embedding_model: e.target.value })} />
              : <select value={form.embedding_model} disabled={modelsLoading}
              onChange={(e) => change({ embedding_model: e.target.value })}>
              {!modelOptions.includes(form.embedding_model) && <option value={form.embedding_model} disabled={models !== null}>
                {form.embedding_model}{models !== null ? ' (non verificato)' : ''}
              </option>}
              {modelOptions.map((model) => <option key={model} value={model}>{model}</option>)}
            </select>}
          </label>
          {form.embedding_provider === 'compatible' && <datalist id="embedding-available-models">
            {modelOptions.map((model) => <option key={model} value={model} />)}
          </datalist>}
          <div className="ai-actions">
            <button className="ai-button" type="button" disabled={modelsLoading} onClick={() => {
              if (!validEmbeddingService()) return
              void loadModels(form)
            }}>{modelsLoading ? 'Caricamento modelli…' : 'Ricarica modelli'}</button>
          </div>
          {modelsError && <p className="ai-error" role="alert">{modelsError}</p>}
          {!modelsLoading && models !== null && models.length === 0 &&
            <p className="retrieval-description" role="status">{form.embedding_provider === 'compatible'
              ? 'Nessun modello identificato automaticamente. Inserisci il nome del modello di embedding.'
              : 'Nessun modello di embedding rilevato su questo server.'}</p>}
          {!modelsLoading && models === null && !modelsError &&
            <p className="retrieval-description">Ricarica i modelli dopo aver modificato il provider o il collegamento.</p>}
          {modelsLoading && <p className="retrieval-description" role="status">Lettura dei modelli disponibili…</p>}
          {!(semantic && saved?.backend === 'qdrant') &&
            <p className="retrieval-description">Usato dalla ricerca semantica.</p>}
          <details className="retrieval-technical" open={embeddingOpen}
            onToggle={(event) => setEmbeddingOpen(event.currentTarget.open)}>
            <summary>Impostazioni avanzate</summary>
            <div ref={embeddingServiceRef} className="retrieval-embedding-service">
              <ServiceAddressFields name="embedding_url" value={form.embedding_url} onChange={(value) => change({ embedding_url: value })}
                label={form.embedding_provider === 'ollama' ? 'Indirizzo Ollama' : 'Indirizzo del servizio embedding'}
                defaultPort={form.embedding_provider === 'ollama' ? '11434' : undefined} serviceName="Ollama in locale" />
              <label><span id="retrieval-embedding-key-label">Chiave del servizio embedding{provider?.requires_key ? '' : ' (facoltativa)'}</span>
                <input type="password" autoComplete="new-password" maxLength={4096}
                  required={provider?.requires_key && (!saved?.has_embedding_api_key || !sameEmbeddingService || !!form.clear_embedding_api_key)}
                  aria-labelledby="retrieval-embedding-key-label" aria-describedby="retrieval-embedding-key-help"
                  disabled={!!form.clear_embedding_api_key && !!sameEmbeddingService && !provider?.requires_key} value={form.embedding_api_key}
                  onChange={(e) => change({ embedding_api_key: e.target.value, clear_embedding_api_key: false })} />
                <small id="retrieval-embedding-key-help">{saved?.has_embedding_api_key && sameEmbeddingService && !form.clear_embedding_api_key
                  ? 'Chiave salvata. Lascia vuoto per conservarla.' : 'Chiave del provider di embedding, separata da quella della chat.'}</small>
              </label>
              {saved?.has_embedding_api_key && <label className="ai-checkbox">
                <input type="checkbox" checked={form.clear_embedding_api_key}
                  onChange={(e) => change({ clear_embedding_api_key: e.target.checked, embedding_api_key: '' })} />Rimuovi chiave embedding
              </label>}
              {embeddingKeyPending &&
                <p className="retrieval-warning">Indirizzo modificato: reinserisci o rimuovi la chiave embedding salvata.</p>}
              {form.embedding_provider !== 'ollama' && <p className="retrieval-description">Il servizio scelto riceverà i testi da indicizzare. L’utilizzo può avere un costo.</p>}
              <div className="retrieval-connection">
                <div className="ai-actions">
                  <button className="ai-button" type="button" disabled={modelsLoading} onClick={() => {
                    if (validEmbeddingService()) void loadModels(form, true)
                  }}>{connection?.kind === 'checking' ? 'Verifica…' : 'Verifica collegamento'}</button>
                </div>
                <p className="retrieval-description">Controlla l’accesso al servizio e l’elenco dei modelli, senza generare embedding.</p>
                {connection && <p role={connection.kind === 'error' ? 'alert' : 'status'}
                  className={connection.kind === 'error' ? 'ai-error' : connection.kind === 'warning' ? 'retrieval-warning' : 'ai-notice'}>
                  {connection.message}
                </p>}
              </div>
            </div>
          </details>
        </section>

        <section className="settings-card ai-settings retrieval-card" aria-labelledby="retrieval-heading">
          <h2 id="retrieval-heading">Ricerca nelle fonti</h2>
          <label>Metodo di ricerca
            <select value={form.backend} onChange={(e) => change({ backend: e.target.value as RetrievalInput['backend'] })}>
              <option value="fts5">Per parole chiave</option>
              <option value="qdrant">Semantica</option>
            </select>
          </label>
          {semantic && <details className="retrieval-technical" open={searchOpen}
            onToggle={(event) => setSearchOpen(event.currentTarget.open)}>
            <summary>Impostazioni avanzate</summary>
            <fieldset className="retrieval-tech-group" aria-label="Configurazione archivio">
              <label>Tipo di archivio
                <select value={form.qdrant_mode} onChange={(e) => change({ qdrant_mode: e.target.value as RetrievalInput['qdrant_mode'] })}>
                  <option value="local">Integrato nell’applicazione</option>
                  <option value="remote">Server Qdrant esterno</option>
                </select>
              </label>
              {form.qdrant_mode === 'remote' && <>
                <ServiceAddressFields name="qdrant_url" value={form.qdrant_url} onChange={(value) => change({ qdrant_url: value })}
                  label="Indirizzo Qdrant" defaultPort="6333" serviceName="Qdrant" />
                <label><span id="retrieval-qdrant-key-label">Chiave Qdrant (facoltativa)</span>
                  <input type="password" autoComplete="new-password" maxLength={4096}
                    aria-labelledby="retrieval-qdrant-key-label" aria-describedby="retrieval-qdrant-key-help"
                    disabled={form.clear_qdrant_api_key} value={form.qdrant_api_key}
                    onChange={(e) => change({ qdrant_api_key: e.target.value, clear_qdrant_api_key: false })} />
                  <small id="retrieval-qdrant-key-help">{saved?.has_qdrant_api_key ? 'Chiave salvata. Lascia vuoto per conservarla.' : 'Richiesta solo se il server è protetto.'}</small>
                </label>
                {saved?.has_qdrant_api_key && <label className="ai-checkbox">
                  <input type="checkbox" checked={form.clear_qdrant_api_key}
                    onChange={(e) => change({ clear_qdrant_api_key: e.target.checked, qdrant_api_key: '' })} />Rimuovi chiave Qdrant
                </label>}
                {qdrantKeyPending &&
                  <p className="retrieval-warning">Indirizzo modificato: reinserisci o rimuovi la chiave Qdrant salvata.</p>}
              </>}
            </fieldset>
            <div className="retrieval-connection">
              <div className="ai-actions">
                <button className="ai-button" type="button" onClick={() => void perform('check')}>{busy === 'check' ? 'Verifica…' : 'Verifica ricerca semantica'}</button>
              </div>
              <p className="retrieval-description">Verifica il modello e l’archivio senza aggiornare l’indice.</p>
            </div>
            <section className="retrieval-maintenance" aria-labelledby="retrieval-maintenance-heading">
              <div className="retrieval-maintenance-head">
                <h3 id="retrieval-maintenance-heading">Manutenzione dell’indice</h3>
                <p className="retrieval-description">L’indice si aggiorna prima delle ricerche semantiche.
                  Puoi prepararlo qui in anticipo, per tutti i progetti e le fonti condivise.</p>
              </div>
              <button className="ai-button" type="button" disabled={dirty || saveState.kind === 'saving' || saved?.backend !== 'qdrant'}
                onClick={() => void perform('index')}>{busy === 'index' ? 'Aggiornamento indice…' : 'Aggiorna indice'}</button>
              {dirty && <p className="retrieval-description">L’indice si può aggiornare quando le modifiche sono salvate.</p>}
            </section>
          </details>}
          {error && <div className="ai-error" role="alert">{error}</div>}
          {(busy || notice) && <p className="ai-notice" role="status">{busy
            ? { check: 'Verifica del collegamento…', index: 'Aggiornamento dell’indice in corso. L’operazione può richiedere tempo.' }[busy]
            : notice}</p>}
        </section>

        {/* Both cards save themselves; one line below them reports the outcome. */}
        <div className="retrieval-autosave">
          {saveState.kind === 'error'
            ? <div className="ai-error" role="alert">{saveState.message}
              <button className="ai-button" type="button" onClick={requestCommit}>Riprova</button></div>
            : <p className="retrieval-autosave-status" aria-live="polite">{{
              // Nothing to report while idle; the empty region still announces later outcomes.
              idle: '', saving: 'Salvataggio…',
              incomplete: 'Modifiche non salvate: completa i campi indicati.', saved: saveState.message,
            }[saveState.kind]}</p>}
        </div>
      </fieldset>
    </form>}
  </div>
}
