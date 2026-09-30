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
          ? 'Ricerca vettoriale salvata. Le fonti vengono aggiornate prima di ogni ricerca; puoi prepararle anche adesso.'
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
      {form && <form className="ai-profile-form" onSubmit={submit}>
        <fieldset disabled={!!busy}>
          <label>Metodo di ricerca
            <select value={form.backend} onChange={(e) => change({ backend: e.target.value as RetrievalInput['backend'] })}>
              <option value="fts5">Lessicale · FTS5</option>
              <option value="qdrant">Vettoriale · Qdrant</option>
            </select>
          </label>
          {form.backend === 'qdrant' && <>
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
            <label>Modello di embedding
              <input required value={form.embedding_model} onChange={(e) => change({ embedding_model: e.target.value })} />
              <small>Deve essere installato su Ollama e produrre embedding. È separato dal modello della chat.</small>
            </label>
            <details className="ai-advanced">
              <summary>Opzioni avanzate degli embedding</summary>
              <label>Chiave del servizio embedding (facoltativa)
                <input type="password" autoComplete="new-password" value={form.embedding_api_key} onChange={(e) => change({ embedding_api_key: e.target.value })} />
                {saved?.has_embedding_api_key && <small>Chiave salvata. Lascia vuoto per conservarla.</small>}
              </label>
              {saved?.has_embedding_api_key && <label className="ai-checkbox">
                <input type="checkbox" checked={form.clear_embedding_api_key} onChange={(e) => change({ clear_embedding_api_key: e.target.checked })} />Rimuovi chiave embedding
              </label>}
              <label>Prefisso per le domande
                <input value={form.query_prefix} onChange={(e) => change({ query_prefix: e.target.value })} />
              </label>
              <label>Prefisso per i documenti
                <input value={form.document_prefix} onChange={(e) => change({ document_prefix: e.target.value })} />
              </label>
              <p className="ai-help">Compila i prefissi solo se richiesti dal modello. Cambiare modello o prefissi prepara un nuovo indice.</p>
            </details>
          </>}
          <div className="ai-actions">
            <button className="ai-button ai-button-primary" type="submit">{busy === 'save' ? 'Salvataggio…' : 'Salva ricerca'}</button>
            {form.backend === 'qdrant' && <>
              <button className="ai-button" type="button" onClick={() => void perform('check')}>{busy === 'check' ? 'Verifica…' : 'Verifica collegamento'}</button>
              <button className="ai-button" type="button" disabled={dirty} onClick={() => void perform('index')}>{busy === 'index' ? 'Preparazione indice…' : 'Aggiorna indice'}</button>
            </>}
          </div>
          {form.backend === 'qdrant' && dirty && <small>Salva le impostazioni prima di aggiornare l’indice.</small>}
        </fieldset>
      </form>}
      {error && <p className="ai-error" role="alert">{error}{!form && <button className="ai-button" onClick={() => setAttempt((value) => value + 1)}>Riprova</button>}</p>}
      {notice && <p className="ai-notice" role="status">{notice}</p>}
    </section>
  )
}
