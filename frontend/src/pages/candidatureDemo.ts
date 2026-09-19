export const FIELDS = [
  { key: 'ente', label: 'Ente proponente', source: 'Scheda progetto', value: 'Comune di Valleverde' },
  { key: 'intervento', label: 'Intervento', source: 'Scheda progetto', value: 'Riqualificazione della scuola primaria di via Roma' },
  { key: 'supporto', label: 'Supporto tecnico', source: 'Company KB', value: 'Mapi Ingegneria' },
  { key: 'responsabile', label: 'Responsabile del procedimento', source: '', value: '' },
  { key: 'importo', label: 'Importo richiesto (EUR)', source: '', value: '' },
] as const
export type FieldKey = typeof FIELDS[number]['key']
export type Values = Record<FieldKey, string>
export const EMPTY_VALUES: Values = { ente: '', intervento: '', supporto: '', responsabile: '', importo: '' }
export const DEMO_VALUES: Values = { ...EMPTY_VALUES, ente: FIELDS[0].value, intervento: FIELDS[1].value, supporto: FIELDS[2].value }

export function fieldIsValid(key: FieldKey, value: string) {
  if (!value.trim()) return false
  if (key !== 'importo') return true
  return Number.isFinite(Number(value)) && Number(value) > 0
}

export function displayValue(key: FieldKey, value: string) {
  if (key !== 'importo' || !fieldIsValid(key, value)) return value
  return new Intl.NumberFormat('it-IT', { style: 'currency', currency: 'EUR' }).format(Number(value))
}

export function facsimileHtml(values: Values) {
  const output = document.implementation.createHTMLDocument('Facsimile candidatura - DEMO')
  output.documentElement.lang = 'it'
  const charset = output.createElement('meta')
  charset.setAttribute('charset', 'utf-8')
  output.head.append(charset)
  const style = output.createElement('style')
  style.textContent = 'body{font:16px/1.6 system-ui,sans-serif;color:#222;max-width:760px;margin:40px auto;padding:24px}header{border-bottom:2px solid #444;padding-bottom:16px}h1{font-size:26px}dt{font-weight:600;margin-top:20px}dd{margin:4px 0;white-space:pre-wrap;overflow-wrap:anywhere}footer{margin-top:40px;border-top:1px solid #aaa;padding-top:16px;font-size:13px}@media print{body{margin:0;padding:0}}'
  output.head.append(style)
  const header = output.createElement('header')
  header.textContent = 'FACSIMILE DIMOSTRATIVO - NON UTILIZZABILE PER INVII UFFICIALI'
  const title = output.createElement('h1')
  title.textContent = 'Istanza di candidatura'
  const fields = output.createElement('dl')
  for (const field of FIELDS) {
    const label = output.createElement('dt')
    label.textContent = field.label
    const value = output.createElement('dd')
    value.textContent = displayValue(field.key, values[field.key])
    fields.append(label, value)
  }
  const footer = output.createElement('footer')
  footer.textContent = 'Simulazione del flusso di Mapi RAG. Dati fittizi o inseriti durante la demo; nessuna estrazione da documenti o verifica di ammissibilita.'
  output.body.append(header, title, fields, footer)
  return `<!doctype html>\n${output.documentElement.outerHTML}`
}
