import { useEffect, useRef, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { EmbeddingProvider, EmbeddingProviderDefinition, RetrievalInput, RetrievalSettings } from '../types'
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

export function RetrievalSettingsPanel() {
  const [saved, setSaved] = useState<RetrievalSettings | null>(null)
  const [providers, setProviders] = useState<EmbeddingProviderDefinition[]>([])
  const [form, setForm] = useState<RetrievalInput | null>(null)
  const [busy, setBusy] = useState<'save' | 'check' | 'index' | ''>('')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState('')
  const [attempt, setAttempt] = useState(0)
  const [searchOpen, setSearchOpen] = useState(false)
  const [embeddingOpen, setEmbeddingOpen] = useState(false)
  const [models, setModels] = useState<string[] | null>(null)
  const [modelsLoading, setModelsLoading] = useState(false)
  const [modelsError, setModelsError] = useState('')
  const modelsRequest = useRef<AbortController | null>(null)
  const formRef = useRef<HTMLFormElement>(null)

  async function loadModels(config: RetrievalInput) {
    modelsRequest.current?.abort()
    const controller = new AbortController()
    modelsRequest.current = controller
    setModels(null)
    setModelsLoading(true)
    setModelsError('')
    try {
      const result = await api.embeddingModels({
        embedding_provider: config.embedding_provider,
        embedding_url: config.embedding_url, embedding_api_key: config.embedding_api_key,
        clear_embedding_api_key: config.clear_embedding_api_key,
      }, controller.signal)
      if (!controller.signal.aborted) setModels(result.models)
    } catch (reason) {
      if (!controller.signal.aborted) setModelsError(reason instanceof Error ? reason.message : 'Modelli non disponibili')
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
  const indexConfigChanged = !!saved && !!form && (
    form.embedding_provider !== (saved.embedding_provider ?? 'ollama') ||
    form.embedding_model !== saved.embedding_model || form.embedding_url !== saved.embedding_url ||
    form.qdrant_mode !== saved.qdrant_mode ||
    (form.qdrant_mode === 'remote' && form.qdrant_url !== saved.qdrant_url)
  )
  const modelOptions = [...new Set((models ?? []).map((name) =>
    form && (name === form.embedding_model || form.embedding_provider === 'ollama' && sameModel(name, form.embedding_model))
      ? form.embedding_model : name))]

  function change(patch: Partial<RetrievalInput>) {
    if ('embedding_provider' in patch || 'embedding_url' in patch || 'embedding_api_key' in patch || 'clear_embedding_api_key' in patch) {
      modelsRequest.current?.abort()
      setModels(null); setModelsLoading(false); setModelsError('')
    }
    setForm((value) => value ? { ...value, ...patch } : value)
    setNotice('')
    setError(null)
  }

  function changeProvider(id: EmbeddingProvider) {
    const selected = providers.find((item) => item.id === id)
    if (!selected || id === form?.embedding_provider) return
    change({ embedding_provider: id, embedding_url: selected.base_url,
      embedding_model: selected.default_model, embedding_api_key: '',
      clear_embedding_api_key: !!saved?.has_embedding_api_key })
    setEmbeddingOpen(true)
  }

  async function perform(action: 'save' | 'check' | 'index') {
    if (!form || busy) return
    if (action === 'check' && !formRef.current?.reportValidity()) return
    if (action === 'index' && (dirty || !semantic || saved?.backend !== 'qdrant')) return
    setBusy(action)
    setError(null)
    setNotice('')
    try {
      if (action === 'save') {
        const settings = await api.saveRetrievalSettings(form)
        setSaved(settings)
        setForm(formValue(settings))
        if (settings.embedding_url !== saved?.embedding_url || settings.embedding_provider !== saved?.embedding_provider || form.embedding_api_key || form.clear_embedding_api_key) {
          void loadModels(formValue(settings))
        }
        setNotice(settings.backend === 'qdrant'
          ? 'Impostazioni salvate. L’indice verrà sincronizzato alla prossima ricerca semantica; puoi aggiornarlo prima dalla manutenzione.'
          : 'Impostazioni salvate. La ricerca usa le parole chiave.')
      } else if (action === 'check') {
        const result = await api.checkRetrievalConnection(form)
        setNotice(result.message)
      } else {
        const result = await api.updateVectorIndex()
        setNotice(`Indice aggiornato: ${result.indexed_chunks} frammenti, ${result.updated_chunks} aggiornati e ${result.deleted_chunks} rimossi.`)
      }
    } catch (reason) {
      const context = { save: 'Salvataggio non riuscito', check: 'Verifica non riuscita', index: 'Aggiornamento indice non riuscito' }
      setError(`${context[action]}: ${reason instanceof Error ? reason.message : 'riprova.'}`)
    } finally {
      setBusy('')
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void perform('save')
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
      onInvalidCapture={() => { setSearchOpen(true); setEmbeddingOpen(true) }} aria-busy={!!busy}>
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
              const input = formRef.current?.elements.namedItem('embedding_url') as HTMLInputElement | null
              if (input && !input.reportValidity()) return
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
          {semantic ? <p className="retrieval-model-summary">{saved?.backend === 'qdrant'
            ? <>Modello attivo: <strong>{saved.embedding_model}</strong></>
            : <>Modello previsto: <strong>{form.embedding_model}</strong></>}</p>
            : <p className="retrieval-description">Usato dalla ricerca semantica.</p>}
          <details className="retrieval-technical" open={embeddingOpen}
            onToggle={(event) => setEmbeddingOpen(event.currentTarget.open)}>
            <summary>Impostazioni avanzate</summary>
            <div className="retrieval-embedding-service">
              <label>{form.embedding_provider === 'ollama' ? 'Indirizzo Ollama' : 'Indirizzo del servizio embedding'}
                <input name="embedding_url" required type="url" maxLength={500} value={form.embedding_url}
                  onChange={(e) => change({ embedding_url: e.target.value })} />
              </label>
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
              {saved?.has_embedding_api_key && !sameEmbeddingService &&
                !form.clear_embedding_api_key && !form.embedding_api_key?.trim() &&
                <p className="retrieval-warning">Indirizzo modificato: reinserisci o rimuovi la chiave embedding salvata.</p>}
              {(form.embedding_provider === 'ollama' || form.embedding_provider === 'compatible') &&
                <p className="retrieval-description">127.0.0.1 e localhost indicano la macchina del backend, non necessariamente il tuo computer.</p>}
              {form.embedding_provider !== 'ollama' && <p className="retrieval-description">Il servizio scelto riceverà i testi da indicizzare. L’utilizzo può avere un costo.</p>}
            </div>
          </details>
          {semantic && indexConfigChanged && <p className="retrieval-warning">
            Questa modifica può richiedere un nuovo indice. Il salvataggio non lo prepara:
            avverrà alla prossima ricerca semantica oppure con «Aggiorna indice».
          </p>}
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
            <fieldset className="retrieval-tech-group">
              <legend>Archivio vettoriale</legend>
              <label>Tipo di archivio
                <select value={form.qdrant_mode} onChange={(e) => change({ qdrant_mode: e.target.value as RetrievalInput['qdrant_mode'] })}>
                  <option value="local">Integrato nell’applicazione</option>
                  <option value="remote">Server Qdrant esterno</option>
                </select>
              </label>
              {form.qdrant_mode === 'remote' && <>
                <label>Indirizzo Qdrant
                  <input required type="url" maxLength={500} value={form.qdrant_url}
                    onChange={(e) => change({ qdrant_url: e.target.value })} />
                </label>
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
                {saved?.has_qdrant_api_key && form.qdrant_url !== saved.qdrant_url &&
                  !form.clear_qdrant_api_key && !form.qdrant_api_key?.trim() &&
                  <p className="retrieval-warning">Indirizzo modificato: reinserisci o rimuovi la chiave Qdrant salvata.</p>}
              </>}
            </fieldset>
            <div className="retrieval-connection">
              <div className="ai-actions">
                <button className="ai-button" type="button" onClick={() => void perform('check')}>{busy === 'check' ? 'Verifica…' : 'Verifica collegamento'}</button>
              </div>
              <p className="retrieval-description">Verifica il modello e l’archivio senza salvare le impostazioni o aggiornare l’indice.</p>
            </div>
            <section className="retrieval-maintenance" aria-labelledby="retrieval-maintenance-heading">
              <h3 id="retrieval-maintenance-heading">Manutenzione dell’indice</h3>
              <p className="retrieval-description">L’indice si aggiorna prima delle ricerche semantiche.
                Puoi prepararlo qui in anticipo, per tutti i progetti e le fonti condivise.</p>
              <button className="ai-button" type="button" disabled={dirty || saved?.backend !== 'qdrant'}
                onClick={() => void perform('index')}>{busy === 'index' ? 'Aggiornamento indice…' : 'Aggiorna indice'}</button>
              {dirty && <p className="retrieval-description">Salva le impostazioni prima di aggiornare l’indice.</p>}
            </section>
          </details>}
          <div className="ai-actions retrieval-save">
            <button className="ai-button ai-button-primary" type="submit">{busy === 'save' ? 'Salvataggio…' : 'Salva impostazioni'}</button>
            {dirty && <span className="retrieval-unsaved">Modifiche non salvate</span>}
          </div>
          {error && <div className="ai-error" role="alert">{error}</div>}
          {(busy || notice) && <p className="ai-notice" role="status">{busy
            ? { save: 'Salvataggio delle impostazioni…', check: 'Verifica del collegamento…', index: 'Aggiornamento dell’indice in corso. L’operazione può richiedere tempo.' }[busy]
            : notice}</p>}
        </section>

      </fieldset>
    </form>}
  </div>
}
