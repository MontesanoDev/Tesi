import { useEffect, useState, type FormEvent } from 'react'
import { api } from '../api'
import type { AiLoginFlow, AiProfile, AiProfileInput, AiProvider, AiProviderDefinition, AiSettings } from '../types'
import './AiSettings.css'

function message(reason: unknown) {
  return reason instanceof Error ? reason.message : 'Operazione non riuscita. Riprova.'
}

function ProfileForm({ profile, providers, onSaved, onCancel }: {
  providers: AiProviderDefinition[]
  profile: AiProfile | null
  onSaved: (profile: AiProfile) => void
  onCancel: () => void
}) {
  const [form, setForm] = useState<AiProfileInput | null>(() => profile ? ({
    name: profile.name, provider: profile.provider, base_url: profile.base_url,
    model: profile.model, context_window: profile.context_window, api_key: '', clear_api_key: false,
  }) : null)
  const [models, setModels] = useState<string[]>([])
  const [busy, setBusy] = useState<'check' | 'save' | 'login' | null>(null)
  const [login, setLogin] = useState<AiLoginFlow | null>(null)
  const [code, setCode] = useState('')
  const service = providers.find((item) => item.id === form?.provider)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  function update(patch: Partial<AiProfileInput>) {
    setForm((current) => current ? ({ ...current, ...patch }) : null)
    setNotice(null)
    setError(null)
  }
  function changeService(provider: AiProvider) {
    const selected = providers.find((item) => item.id === provider)
    if (!selected) return
    setForm({ provider, name: selected.name, base_url: selected.base_url, model: '', api_key: '',
      context_window: form?.context_window ?? 32768, clear_api_key: !!profile?.has_api_key })
    setNotice(null); setError(null)
    setModels([]); setLogin(null); setCode('')
  }
  async function discover(candidate: AiProfileInput) {
    const result = await api.checkAiConnection({ ...candidate, profile_id: profile?.id,
      name: candidate.name.trim() || 'Modello AI', model: candidate.model.trim() || 'discovery' })
    setModels(result.models)
    if (result.models.length && !result.models.includes(candidate.model)) {
      setForm((current) => current ? ({ ...current, model: result.models[0] }) : null)
    }
    setNotice(result.message)
  }
  async function check() {
    if (!form) return
    setBusy('check'); setError(null); setNotice(null)
    try { await discover(form) }
    catch (reason) { setError(message(reason)) }
    finally { setBusy(null) }
  }
  async function beginLogin() {
    setBusy('login'); setError(null); setNotice(null); setCode(''); setLogin(null)
    update({ connection_token: undefined })
    try { setLogin(await api.beginOpenRouterLogin()) }
    catch (reason) { setError(message(reason)) }
    finally { setBusy(null) }
  }
  async function finishLogin() {
    if (!login || !code.trim() || !form || !service) return
    setBusy('login'); setError(null); setNotice(null)
    try {
      await api.completeOpenRouterLogin(login.connection_token, code.trim())
      const candidate = { ...form, api_key: '', clear_api_key: false,
        base_url: service.base_url, connection_token: login.connection_token }
      setForm(candidate); setLogin(null); setCode('')
      await discover(candidate)
    } catch (reason) { setError(message(reason)) }
    finally { setBusy(null) }
  }
  async function save(event: FormEvent) {
    event.preventDefault()
    if (busy || !form) return
    setBusy('save'); setError(null)
    try { onSaved(await api.saveAiProfile(form, profile?.id)) }
    catch (reason) { setError(message(reason)) }
    finally { setBusy(null) }
  }
  return <form className="ai-profile-form" onSubmit={save} aria-label={profile ? 'Modifica modello' : 'Nuovo modello'}>
    <h3>{profile ? 'Modifica modello' : 'Aggiungi un modello'}</h3>
    <fieldset disabled={!!busy}>
      <label>Servizio
        <select value={form?.provider ?? ''} onChange={(event) => changeService(event.target.value as AiProvider)}>
          <option value="" disabled>Seleziona un servizio</option>
          {providers.map((item) => <option key={item.id} value={item.id}>{item.name}</option>)}
        </select>
      </label>
      {form && service && <>
      <p className="ai-help ai-provider-description">{service.description}</p>
      <label>Nome da mostrare
        <input required maxLength={100} value={form.name} onChange={(event) => update({ name: event.target.value })}
          placeholder="Ad esempio: Ollama ufficio" />
      </label>
      {service.browser_login && <div className="ai-account-connect">
        <strong>Collega il tuo account OpenRouter</strong>
        <p>Accedi dal browser, poi incolla qui il codice mostrato da OpenRouter.
          L'utilizzo dei modelli viene addebitato sul tuo account OpenRouter.</p>
        {form.connection_token && <p className="ai-notice" role="status">Account collegato. Scegli il modello e salva.</p>}
        <button className="ai-button" type="button" onClick={() => void beginLogin()}>
          {busy === 'login' ? 'Collegamento…' : login || form.connection_token ? 'Ricomincia accesso' : 'Accedi con OpenRouter'}
        </button>
        {login && <div className="ai-login-steps">
          <a href={login.authorization_url} target="_blank" rel="noopener noreferrer">Apri accesso OpenRouter ↗</a>
          <label>Codice di autorizzazione
            <input type="password" autoComplete="off" maxLength={4096} value={code}
              onChange={(event) => setCode(event.target.value)} placeholder="Incolla il codice mostrato dopo l'accesso" />
          </label>
          <button type="button" className="ai-button" disabled={!code.trim()} onClick={() => void finishLogin()}>Collega account</button>
          <small>Il codice scade dopo 10 minuti. Dopo il collegamento, salva il modello entro 10 minuti.</small>
        </div>}
      </div>}
      {(form.provider !== 'ollama' || profile?.has_api_key) && !form.connection_token && <label>
        {service.browser_login ? 'Oppure usa una chiave API' : `Chiave API${service.requires_key ? '' : ' (facoltativa)'}`}
        <input type="password" autoComplete="new-password" maxLength={4096} value={form.api_key}
          aria-label={service.requires_key ? 'Chiave API' : 'Chiave API (facoltativa)'}
          required={service.requires_key && (!profile?.has_api_key || !!form.clear_api_key)}
          placeholder={profile?.has_api_key && !form.clear_api_key ? 'Chiave già salvata' : 'Incolla la chiave del servizio'}
          onChange={(event) => update({ api_key: event.target.value, clear_api_key: false })} />
        <small>{profile?.has_api_key && !form.clear_api_key
          ? 'Lascia vuoto per mantenere la chiave salvata.'
          : 'La chiave viene salvata sul server e non viene mostrata dopo il salvataggio.'}</small>
        {service.credentials_url && <a className="ai-credentials-link" href={service.credentials_url} target="_blank" rel="noopener noreferrer">
          Ottieni una chiave da {service.name} ↗
        </a>}
      </label>}
      {profile?.has_api_key && !service.requires_key && <label className="ai-checkbox">
        <input type="checkbox" checked={!!form.clear_api_key}
          onChange={(event) => update({ clear_api_key: event.target.checked, api_key: '' })} />Rimuovi la chiave salvata
      </label>}
      {(form.provider === 'openai' || form.provider === 'anthropic') && <p className="ai-help">
        Serve una chiave API del servizio. L'abbonamento a ChatGPT o Claude non include automaticamente questo utilizzo.
      </p>}
      {form.provider === 'ollama' && <p className="ai-help">Ollama può essere sul computer che esegue Mapi
        oppure su un server remoto. I modelli devono essere installati sul server Ollama scelto.</p>}
      {(form.provider === 'compatible' || form.provider === 'ollama') && <label>Indirizzo del servizio
        <input type="url" required value={form.base_url}
          placeholder={form.provider === 'ollama' ? 'http://192.168.1.50:11434' : 'https://servizio.example/v1'}
          onChange={(event) => { update({ base_url: event.target.value, connection_token: undefined }); setModels([]) }} />
        <small>{form.provider === 'ollama'
          ? '127.0.0.1 indica il computer che esegue Mapi. Per un servizio remoto usa il suo IP o dominio, raggiungibile da Mapi.'
          : "Usa l'indirizzo base delle API compatibili con Chat Completions, spesso terminante in /v1."}</small>
      </label>}
      <div className="ai-actions">
        <button type="button" className="ai-button" onClick={() => void check()}>
          {busy === 'check' ? 'Verifica in corso…' : 'Verifica collegamento e trova modelli'}
        </button>
      </div>
      <small className="ai-help">La verifica legge l'elenco dei modelli. Non invia documenti e non genera testo.</small>
      <label>Modello
        <input required maxLength={160} list="ai-available-models" value={form.model}
          placeholder="Scegli un modello o inserisci il suo nome"
          onChange={(event) => update({ model: event.target.value })} />
        <datalist id="ai-available-models">{models.map((model) => <option value={model} key={model} />)}</datalist>
      </label>
      {models.length > 0 && <label>Modelli disponibili
        <select value={models.includes(form.model) ? form.model : ''} onChange={(event) => update({ model: event.target.value })}>
          <option value="" disabled>Scegli dall'elenco</option>
          {models.map((model) => <option value={model} key={model}>{model}</option>)}
        </select>
      </label>}
      <details className="ai-advanced">
        <summary>Opzioni avanzate</summary>
        {form.provider !== 'compatible' && form.provider !== 'ollama' && <label>Indirizzo del servizio
          <input type="url" required value={form.base_url}
            onChange={(event) => { update({ base_url: event.target.value, connection_token: undefined }); setModels([]) }} />
          <small>Indirizzo base delle API {service.name}.</small>
        </label>}
        {form.provider === 'ollama' && <label>Finestra di contesto (token)
          <input type="number" required min={2048} max={1048576} step={1} value={form.context_window}
            onChange={(event) => update({ context_window: Number(event.target.value) })} />
          <small>Deve contenere istruzioni, fonti e risposta. Aumentarla richiede più memoria;
            la capacità effettiva dipende dal modello e dal computer.</small>
        </label>}
      </details>
      </>}
      <div className="ai-actions">
        {form && service && <button className="ai-button ai-button-primary" type="submit">{busy === 'save' ? 'Salvataggio…' : 'Salva modello'}</button>}
        <button className="ai-button" type="button" onClick={onCancel}>Annulla</button>
      </div>
    </fieldset>
    {error && <p className="ai-error" role="alert">{error}</p>}
    {notice && <p className="ai-notice" role="status">{notice}</p>}
  </form>
}

export function AiSettingsPanel() {
  const [settings, setSettings] = useState<AiSettings | null>(null)
  const [editor, setEditor] = useState<AiProfile | 'new' | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [reload, setReload] = useState(0)
  useEffect(() => {
    const controller = new AbortController()
    setError(null)
    api.aiSettings(controller.signal).then((data) => {
      if (!controller.signal.aborted) setSettings(data)
    }).catch((reason) => { if (!controller.signal.aborted) setError(message(reason)) })
    return () => controller.abort()
  }, [reload])
  async function makeDefault(id: string) {
    setBusy(true); setError(null); setNotice(null)
    try { setSettings(await api.setDefaultAiProfile(id)); setNotice('Modello predefinito aggiornato.') }
    catch (reason) { setError(message(reason)) }
    finally { setBusy(false) }
  }
  async function remove(profile: AiProfile) {
    if (!window.confirm(`Eliminare il modello “${profile.name}”?${settings?.default_profile_id === profile.id
      ? ' I progetti che usano il predefinito resteranno senza modello finché non ne scegli un altro.' : ''}`)) return
    setBusy(true); setError(null); setNotice(null)
    try {
      await api.deleteAiProfile(profile.id)
      setSettings((current) => current && ({
        ...current, profiles: current.profiles.filter((item) => item.id !== profile.id),
        default_profile_id: current.default_profile_id === profile.id ? null : current.default_profile_id,
      }))
      setNotice('Modello eliminato.')
    } catch (reason) { setError(message(reason)) }
    finally { setBusy(false) }
  }
  function saved(profile: AiProfile) {
    setSettings((current) => {
      const existing = current?.profiles ?? []
      return {
        ...current, profiles: existing.some((item) => item.id === profile.id)
          ? existing.map((item) => item.id === profile.id ? profile : item) : [...existing, profile],
        default_profile_id: existing.length ? current?.default_profile_id ?? null : profile.id,
      }
    })
    setEditor(null); setNotice('Modello salvato. Puoi selezionarlo in qualsiasi progetto.')
  }
  return <section className="settings-card general-card ai-settings" aria-labelledby="ai-settings-title">
    <h2 id="ai-settings-title">Modelli AI</h2>
    <p>Configura i servizi da usare per la chat, l'estrazione dei dati e la compilazione dei documenti.
      In ogni progetto puoi scegliere uno dei modelli salvati.</p>
    {error && <div className="ai-error" role="alert">{error}
      {!settings && <button className="ai-button" onClick={() => setReload((value) => value + 1)}>Riprova</button>}
    </div>}
    {notice && !editor && <p className="ai-notice" role="status">{notice}</p>}
    {!settings && !error && <p role="status">Caricamento modelli…</p>}
    {settings && <>
      {settings.profiles.length === 0 && <p className="ai-empty">Nessun modello configurato. Scegli un servizio per iniziare.</p>}
      {settings.profiles.length > 0 && !settings.default_profile_id && <p className="ai-help">Scegli un predefinito per i progetti senza un modello specifico.</p>}
      <ul className="ai-profile-list">{settings.profiles.map((profile) => <li key={profile.id}>
        <div className="ai-profile-description"><strong>{profile.name}</strong>
          {settings.default_profile_id === profile.id && <span className="ai-badge">Predefinito</span>}
          <small>{settings.providers?.find((item) => item.id === profile.provider)?.name ?? profile.provider} · {profile.model}</small>
          <small>{profile.has_api_key ? 'Chiave API salvata' : 'Senza chiave API'}</small>
        </div>
        <div className="ai-actions">
          <button className="ai-button" disabled={busy || !!editor || !settings.providers?.length} onClick={() => { setEditor(profile); setNotice(null); setError(null) }}>Modifica</button>
          {settings.default_profile_id !== profile.id && <button className="ai-button" disabled={busy || !!editor} onClick={() => void makeDefault(profile.id)}>Usa come predefinito</button>}
          <button className="ai-button ai-button-danger" disabled={busy || !!editor} onClick={() => void remove(profile)}>Elimina</button>
        </div>
      </li>)}</ul>
      {editor ? <ProfileForm key={editor === 'new' ? 'new' : editor.id}
        providers={settings.providers ?? []}
        profile={editor === 'new' ? null : editor} onSaved={saved} onCancel={() => setEditor(null)} />
        : <button className="ai-button ai-button-primary" disabled={busy || !settings.providers?.length} onClick={() => {
          setEditor('new'); setNotice(null); setError(null)
        }}>Aggiungi modello</button>}

    </>}
  </section>
}
