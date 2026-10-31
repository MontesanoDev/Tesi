import { useEffect, useRef, useState } from 'react'

// Keep paths, IPv6 brackets and explicit ports (including :443) as entered.
function splitAddress(value: string) {
  const match = /^(https?:\/\/)?(\[[^\]]+\]|[^/:?#]+)(?::([0-9]+))?([/?#].*)?$/i.exec(value)
  if (!match) return { address: value, port: '' }
  const scheme = match[1] && match[1].toLowerCase() !== 'http://' ? match[1] : ''
  return { address: `${scheme}${match[2]}${match[4] ?? ''}`, port: match[3] ?? '' }
}

function serviceUrl(address: string, port: string) {
  if (!address) return ''
  const url = /^[a-z][a-z\d+.-]*:\/\//i.test(address) ? address : `http://${address}`
  return url.replace(/^([a-z][a-z\d+.-]*:\/\/[^/?#]*)(.*)$/i,
    (_match, host: string, path: string) => `${host}${port ? `:${port}` : ''}${path}`)
}

export function ServiceAddressFields({ value, onChange, label, name, defaultPort, serviceName }: {
  value: string; onChange: (value: string) => void; label: string
  name: 'embedding_url' | 'qdrant_url'; defaultPort?: string; serviceName?: string
}) {
  const [draft, setDraft] = useState(() => ({ value, ...splitAddress(value) }))
  const addressRef = useRef<HTMLInputElement>(null)
  const portRef = useRef<HTMLInputElement>(null)
  // Resync after loading, saving or switching provider; retain partial typing otherwise.
  if (draft.value !== value) setDraft({ value, ...splitAddress(value) })

  useEffect(() => {
    const portValid = !draft.port || /^\d+$/.test(draft.port) && Number(draft.port) >= 1 && Number(draft.port) <= 65535
    portRef.current?.setCustomValidity(portValid ? '' : 'Inserisci una porta da 1 a 65535 oppure lascia vuoto.')
    let addressValid = false
    try {
      const url = new URL(serviceUrl(draft.address, ''))
      addressValid = ['http:', 'https:'].includes(url.protocol) && !!url.hostname &&
        !url.username && !url.password && !url.search && !url.hash &&
        !/\s/.test(draft.address) && draft.value.length <= 500
    } catch { /* Native required validation also handles an empty address. */ }
    addressRef.current?.setCustomValidity(addressValid || !draft.address ? '' :
      'Inserisci un indirizzo valido, ad esempio 127.0.0.1 oppure https://server.example, senza credenziali o parametri.')
  }, [draft])

  function update(address: string, port: string) {
    const next = { address, port, value: serviceUrl(address, port) }
    setDraft(next)
    onChange(next.value)
  }

  return <div className="retrieval-service-address">
    <div className="retrieval-address-row">
      <label>{label}
        <input ref={addressRef} name={name} required type="text" maxLength={500}
          autoCapitalize="none" autoCorrect="off" spellCheck={false} placeholder="127.0.0.1 oppure https://server.example"
          aria-describedby={`${name}-help`} value={draft.address} onChange={(event) => {
            const pasted = splitAddress(event.target.value)
            const secureAddress = /^https:\/\//i.test(event.target.value) && !/^https:\/\//i.test(draft.address)
            update(pasted.address, pasted.port || (secureAddress ? '' : draft.port))
          }} onPaste={(event) => {
            const text = event.clipboardData.getData('text').trim()
            if (/^https?:\/\//i.test(text)) {
              event.preventDefault()
              const pasted = splitAddress(text)
              update(pasted.address, pasted.port)
            }
          }} />
      </label>
      <label>Porta (opzionale)
        <input ref={portRef} name={`${name}-port`} type="text" inputMode="numeric" pattern="[0-9]{1,5}"
          maxLength={5} placeholder={defaultPort ?? 'Es. 8080'} aria-describedby={`${name}-help`}
          value={draft.port} onChange={(event) => update(draft.address, event.target.value)} />
      </label>
    </div>
    <p id={`${name}-help`} className="retrieval-description">{defaultPort && serviceName
      ? `${serviceName} usa normalmente la porta ${defaultPort}. Lascia la porta vuota solo se il servizio non ne richiede una specifica.`
      : 'Lascia la porta vuota se il servizio non ne richiede una specifica. Mantieni https:// per i collegamenti sicuri.'}</p>
  </div>
}
