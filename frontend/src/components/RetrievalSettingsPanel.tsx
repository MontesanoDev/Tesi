import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { api } from '../api'
import type { RetrievalInput, RetrievalSettings } from '../types'
import './AiSettings.css'

function formValue(settings: RetrievalSettings): RetrievalInput {
  const { has_qdrant_api_key: _q, has_embedding_api_key: _e, ...config } = settings
  return { ...config, qdrant_api_key: '', embedding_api_key: '',
    clear_qdrant_api_key: false, clear_embedding_api_key: false }
}

export function RetrievalSettingsPanel() {
  const [saved, setSaved] = useState<RetrievalSettings | null>(null)
  const [form, setForm] = useState<RetrievalInput | null>(null)
  const [busy, setBusy] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState('')
  const [attempt, setAttempt] = useState(0)
  const [advancedOpen, setAdvancedOpen] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    api.retrievalSettings(controller.signal).then((settings) => {
      setSaved(settings)
      setForm(formValue(settings))
      setError(null)
    }).catch((reason: unknown) => {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Ricerca non disponibile')
    })
    return () => controller.abort()
  }, [attempt])

  const dirty = !!saved && JSON.stringify(form) !== JSON.stringify(formValue(saved))
  function change(patch: Partial<RetrievalInput>) {
    setForm((value) => value ? { ...value, ...patch } : value)
    setNotice('')
    setError(null)
  }

  async function perform(action: 'save' | 'check' | 'index') {
    if (!form) return
    setBusy(action)
    setError(null)
    setNotice('')
    try {
      if (action === 'save') {
        const settings = await api.saveRetrievalSettings(form)
        setSaved(settings)
        setForm(formValue(settings))
        setNotice(settings.backend === 'qdrant'
          ? 'Ricerca semantica salvata. Le fonti verranno sincronizzate alla prossima ricerca.'
          : 'Ricerca lessicale salvata.')
      } else if (action === 'check') {
        const result = await api.checkRetrievalConnection(form)
        setNotice(result.message)
      } else {
        const result = await api.updateVectorIndex()
        setNotice(`Indice pronto: ${result.indexed_chunks} frammenti, ${result.updated_chunks} aggiornati e ${result.deleted_chunks} rimossi.`)
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Operazione non riuscita')
    } finally {
      setBusy('')
    }
  }

  function submit(event: FormEvent) {
    event.preventDefault()
    void perform('save')
  }

  return (
    <section className="settings-card ai-settings" aria-labelledby="retrieval-heading">
      <h2 id="retrieval-heading">Ricerca nelle fonti</h2>
      <p>Scegli come la chat trova le informazioni nei documenti.</p>
      {!form && !error && <p role="status">Caricamento ricerca…</p>}
      {form && <form className="ai-profile-form" onSubmit={submit} onInvalidCapture={() => setAdvancedOpen(true)}>
        <fieldset disabled={!!busy}>
          <label>Metodo di ricerca
            <select value={form.backend} onChange={(e) => change({ backend: e.target.value as RetrievalInput['backend'] })}>
              <option value="fts5">Per parole chiave</option>
              <option value="qdrant">Semantica</option>
            </select>
          </label>
          {form.backend === 'qdrant' && <details className="ai-advanced" open={advancedOpen}
            onToggle={(event) => setAdvancedOpen(event.currentTarget.open)}>
            <summary>Impostazioni avanzate</summary>
            <div className="retrieval-advanced-content">
              <p className="ai-help">Modello di embedding: <strong>{form.embedding_model}</strong></p>
              <label>Archivio vettoriale
                <select value={form.qdrant_mode} onChange={(e) => change({ qdrant_mode: e.target.value as RetrievalInput['qdrant_mode'] })}>
                  <option value="local">Locale sul server Mapi</option>
                  <option value="remote">Servizio Qdrant tramite indirizzo</option>
                </select>
              </label>
              {form.qdrant_mode === 'remote' && <>
                <label>Indirizzo Qdrant
                  <input required type="url" value={form.qdrant_url} onChange={(e) => change({ qdrant_url: e.target.value })} />
                </label>
                <label>Chiave Qdrant (facoltativa)
                  <input type="password" autoComplete="new-password" value={form.qdrant_api_key} onChange={(e) => change({ qdrant_api_key: e.target.value })} />
                  {saved?.has_qdrant_api_key && <small>Chiave salvata. Lascia vuoto per conservarla.</small>}
                </label>
                {saved?.has_qdrant_api_key && <label className="ai-checkbox">
                  <input type="checkbox" checked={form.clear_qdrant_api_key} onChange={(e) => change({ clear_qdrant_api_key: e.target.checked })} />Rimuovi chiave Qdrant
                </label>}
              </>}
              <label>Indirizzo Ollama per gli embedding
                <input required type="url" value={form.embedding_url} onChange={(e) => change({ embedding_url: e.target.value })} />
                <small>Servizio locale o remoto raggiungibile da Mapi. 127.0.0.1 indica il server Mapi.</small>
              </label>
              <label>Chiave del servizio embedding (facoltativa)
                <input type="password" autoComplete="new-password" value={form.embedding_api_key} onChange={(e) => change({ embedding_api_key: e.target.value })} />
                {saved?.has_embedding_api_key && <small>Chiave salvata. Lascia vuoto per conservarla.</small>}
              </label>
              {saved?.has_embedding_api_key && <label className="ai-checkbox">
                <input type="checkbox" checked={form.clear_embedding_api_key} onChange={(e) => change({ clear_embedding_api_key: e.target.checked })} />Rimuovi chiave embedding
              </label>}
              <p className="ai-help">Le fonti vengono sincronizzate automaticamente prima della ricerca. Puoi preparare l’indice in anticipo per ridurre l’attesa alla prima domanda.</p>
              <div className="ai-actions">
                <button className="ai-button" type="button" onClick={() => void perform('check')}>{busy === 'check' ? 'Verifica…' : 'Verifica collegamento'}</button>
                <button className="ai-button" type="button" disabled={dirty} onClick={() => void perform('index')}>{busy === 'index' ? 'Preparazione indice…' : 'Aggiorna indice'}</button>
              </div>
              {dirty && <small>Salva le impostazioni prima di aggiornare l’indice.</small>}
            </div>
          </details>}
          <div className="ai-actions">
            <button className="ai-button ai-button-primary" type="submit">{busy === 'save' ? 'Salvataggio…' : 'Salva ricerca'}</button>
          </div>
        </fieldset>
      </form>}
      {error && <p className="ai-error" role="alert">{error}{!form && <button className="ai-button" onClick={() => setAttempt((value) => value + 1)}>Riprova</button>}</p>}
      {notice && <p className="ai-notice" role="status">{notice}</p>}
    </section>
  )
}
