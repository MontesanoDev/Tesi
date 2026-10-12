import { useState } from 'react'
import type { CompilationSession } from '../types'
import './GlobalCompilationReview.css'

export function GlobalCompilationReview({ session, locked, onGenerate }: {
  session: CompilationSession
  locked: boolean
  onGenerate?: (candidateIds: string[], conditions: string[]) => Promise<unknown>
}) {
  const data = session.global_compilation!
  const [selected, setSelected] = useState<string[]>(data.last_review?.candidate_ids ?? [])
  const [confirmed, setConfirmed] = useState<string[]>(data.last_review?.confirmed_condition_ids ?? [])
  const [partialConsent, setPartialConsent] = useState(false)
  const available = data.fields.filter((field) => field.selectable)
  const excluded = data.fields.filter((field) => !field.selectable)
  const requiredConditions = new Set(available.filter((field) => selected.includes(field.candidate_id))
    .flatMap((field) => field.conditions))
  const canGenerate = selected.length > 0 && partialConsent
    && [...requiredConditions].every((id) => confirmed.includes(id))

  function toggle(items: string[], id: string, checked: boolean) {
    return checked ? [...new Set([...items, id])] : items.filter((item) => item !== id)
  }

  return <details className="global-compilation-review">
    <summary>Rivedi proposte e condizioni</summary>
    <p>Seleziona i valori da usare dopo aver controllato la posizione nel modulo e le fonti.
      La selezione è una tua conferma; i valori conservano la provenienza SOURCE.</p>
    <ul>
      {available.map((field) => <li key={field.candidate_id}>
        <label className="global-review-check">
          <input type="checkbox" disabled={locked} checked={selected.includes(field.candidate_id)}
            onChange={(event) => setSelected(toggle(selected, field.candidate_id, event.target.checked))} />
          <span>Usa {field.label}: <strong>{field.value}</strong></span>
        </label>
        {field.conditional && <p>Applicabilità da confermare prima dell’esportazione.</p>}
        <details>
          <summary>Posizione e fonti di {field.label}</summary>
          <p>FORM — {field.form_context || field.form_quote}</p>
          <small>Posizione: {field.candidate_id}</small>
          {field.source_evidence.map((evidence, index) => <p key={index}>
            SOURCE — {evidence.source_name} ({evidence.category === 'company' ? 'Company KB'
              : evidence.category === 'general' ? 'General KB' : 'progetto'}): «{evidence.quote}»
          </p>)}
        </details>
      </li>)}
    </ul>
    {data.conditions.filter((condition) => requiredConditions.has(condition.id)).map((condition) =>
      <label className="global-review-check" key={condition.id}>
        <input type="checkbox" disabled={locked} checked={confirmed.includes(condition.id)}
          onChange={(event) => setConfirmed(toggle(confirmed, condition.id, event.target.checked))} />
        <span>Confermo che si applica al mio caso: {condition.reason || condition.quote}
          <small>FORM: «{condition.quote}»</small></span>
      </label>)}
    {excluded.length > 0 && <details>
      <summary>Proposte escluse o da chiarire ({excluded.length})</summary>
      <ul>{excluded.map((field) => <li key={field.candidate_id}>
        {field.label}: {field.issues.join('; ') || 'Nessun valore utilizzabile verificato.'}
      </li>)}</ul>
    </details>}
    <p>{data.omitted} posizioni non proposte. Non tutte le posizioni sono campi obbligatori.
      Le checkbox non vengono scritte in questa versione.</p>
    <label className="global-review-check">
      <input type="checkbox" disabled={locked} checked={partialConsent}
        onChange={(event) => setPartialConsent(event.target.checked)} />
      <span>Confermo di generare una bozza parziale con i soli valori selezionati.</span>
    </label>
    <button type="button" className="button" disabled={locked || !canGenerate || !onGenerate}
      onClick={() => { void onGenerate?.(selected, confirmed) }}>
      Genera bozza con i valori selezionati
    </button>
  </details>
}
