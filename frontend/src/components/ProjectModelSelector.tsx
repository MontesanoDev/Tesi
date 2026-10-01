import { Check, Settings2, Settings, ArrowUpRight } from 'lucide-react'
import { useEffect, useId, useLayoutEffect, useRef, useState, type KeyboardEvent } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import { useDismissibleMenu } from '../hooks/useDismissibleMenu'
import type { AiSettings, ProjectAiSelection } from '../types'
import './AiSettings.css'

export function ProjectModelSelector({ projectId, disabled = false, onChanging }: {
  projectId: string
  disabled?: boolean
  onChanging?: (changing: boolean) => void
}) {
  const id = useId()
  const [settings, setSettings] = useState<AiSettings | null>(null)
  const [selection, setSelection] = useState<ProjectAiSelection | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [notice, setNotice] = useState<string | null>(null)
  const [reload, setReload] = useState(0)
  const active = useRef<AbortController | null>(null)
  const trigger = useRef<HTMLButtonElement>(null)
  const panel = useRef<HTMLDivElement>(null)
  const [open, setOpen] = useState(false)
  const [placement, setPlacement] = useState({ below: false, maxHeight: 360 })
  const menu = useDismissibleMenu<HTMLDivElement>(open, () => setOpen(false))

  useLayoutEffect(() => {
    if (!open) return
    function position() {
      const rect = trigger.current?.getBoundingClientRect()
      if (!rect) return
      const above = rect.top - 12
      const below = window.innerHeight - rect.bottom - 12
      const placeBelow = above < 260 && below > above
      setPlacement({ below: placeBelow, maxHeight: Math.min(360, Math.max(120, placeBelow ? below : above)) })
    }
    position()
    window.addEventListener('resize', position)
    window.addEventListener('scroll', position, true)
    return () => {
      window.removeEventListener('resize', position)
      window.removeEventListener('scroll', position, true)
    }
  }, [open])

  useEffect(() => {
    if (!open) return
    const selected = panel.current?.querySelector<HTMLElement>('[aria-checked="true"]:not(:disabled)')
    const first = panel.current?.querySelector<HTMLElement>('[role^="menuitem"]:not(:disabled)')
    ;(selected ?? first ?? panel.current)?.focus()
  }, [open, settings])

  function closeMenu() {
    setOpen(false)
    trigger.current?.focus()
  }

  function menuKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key === 'Escape') {
      event.preventDefault(); event.stopPropagation(); closeMenu()
      return
    }
    if (!['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) return
    event.preventDefault()
    const items = [...(panel.current?.querySelectorAll<HTMLElement>('[role^="menuitem"]:not(:disabled)') ?? [])]
    if (!items.length) return
    const index = items.indexOf(document.activeElement as HTMLElement)
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? items.length - 1
      : (index + (event.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length
    items[next]?.focus()
  }
  useEffect(() => {
    const controller = new AbortController()
    active.current = controller
    setSettings(null); setSelection(null); setError(null); setNotice(null); setBusy(false)
    setOpen(false)
    onChanging?.(false)
    Promise.all([api.aiSettings(controller.signal), api.projectAiModel(projectId, controller.signal)])
      .then(([data, selected]) => {
        if (!controller.signal.aborted) { setSettings(data); setSelection(selected) }
      }).catch((reason) => {
        if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : 'Modelli non disponibili')
      })
    return () => { controller.abort(); onChanging?.(false) }
  }, [projectId, reload, onChanging])

  async function select(value: string) {
    if (busy || disabled) return
    const controller = active.current
    setBusy(true); setError(null); setNotice(null); onChanging?.(true)
    try {
      const result = await api.setProjectAiModel(projectId, value || null)
      if (!controller?.signal.aborted) {
        setSelection(result)
        setNotice('Modello aggiornato per questo progetto.')
        closeMenu()
      }
    } catch (reason) {
      if (!controller?.signal.aborted) setError(reason instanceof Error ? reason.message : 'Cambio modello non riuscito')
    } finally {
      if (!controller?.signal.aborted) { setBusy(false); onChanging?.(false) }
    }
  }
  const defaultProfile = settings?.profiles.find((profile) => profile.id === settings.default_profile_id)
  return <div className="composer-ai" ref={menu}
    onBlur={(event) => {
      if (event.relatedTarget && !event.currentTarget.contains(event.relatedTarget)) setOpen(false)
    }}>
    <button ref={trigger} className={`composer-ai-trigger${open ? ' is-open' : ''}`}
      type="button" aria-label="Impostazioni AI" aria-haspopup="menu" aria-expanded={open}
      aria-controls={open ? `${id}-menu` : undefined}
      title={selection?.effective_profile ? `Modello: ${selection.effective_profile.name} · ${selection.effective_profile.model}` : 'Impostazioni AI'}
      onClick={() => setOpen((value) => !value)}
      onKeyDown={(event) => {
        if (event.key === 'ArrowDown' || event.key === 'ArrowUp') { event.preventDefault(); setOpen(true) }
      }}>
      <Settings size={20} strokeWidth={1.7} />
    </button>
    {open && <div ref={panel} id={`${id}-menu`} role="menu" aria-label="Modello AI" tabIndex={-1}
      className={`composer-ai-menu${placement.below ? ' opens-below' : ''}`}
      style={{ maxHeight: placement.maxHeight }} onKeyDown={menuKeyDown}>
      <div className="composer-ai-heading">Modello del progetto</div>
      <div className="composer-ai-options" role="group" aria-label="Modelli configurati">
        {settings && selection ? <>
          <button type="button" role="menuitemradio" aria-checked={selection.profile_id === null}
            className="composer-ai-option" disabled={disabled || busy || !defaultProfile}
            onClick={() => void select('')}>
            <span><strong>Usa predefinito</strong><small>{defaultProfile?.model ?? 'Nessun predefinito configurato'}</small></span>
            {selection.profile_id === null && <Check size={16} aria-hidden="true" />}
          </button>
          {settings.profiles.map((profile) => <button key={profile.id} type="button" role="menuitemradio"
            className="composer-ai-option" aria-checked={selection.profile_id === profile.id}
            disabled={disabled || busy} onClick={() => void select(profile.id)}>
            <span><strong>{profile.name}</strong><small>{profile.model}</small></span>
            {selection.profile_id === profile.id && <Check size={16} aria-hidden="true" />}
          </button>)}
          {settings.profiles.length === 0 && <p className="composer-ai-hint">Aggiungi un modello nelle impostazioni per iniziare.</p>}
        </> : !error && <p className="composer-ai-hint" role="status">Caricamento modelli…</p>}
      </div>
      {disabled && <p className="composer-ai-hint">Attendi la fine della risposta per cambiare modello.</p>}
      {busy && <p className="composer-ai-hint" role="status">Salvataggio…</p>}
      {error && <div className="composer-ai-error" role="alert">{error}
        {!settings && <button type="button" role="menuitem" className="ai-button" onClick={() => setReload((value) => value + 1)}>Riprova</button>}
      </div>}
      <Link role="menuitem" className="composer-ai-manage" to="/settings">
        <Settings2 size={16} aria-hidden="true" /><span>Gestisci modelli</span><ArrowUpRight size={15} aria-hidden="true" />
      </Link>
    </div>}
    {notice && <span className="ai-screen-reader" role="status">{notice}</span>}
  </div>
}
