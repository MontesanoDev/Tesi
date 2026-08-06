import { useState } from 'react'
import { Link } from 'react-router-dom'
import { AppShell } from '../components/AppShell'

export function GeneralSettingsPage() {
  const [reviewRequired, setReviewRequired] = useState(true)

  return (
    <AppShell active="settings">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="settings-page page-container">
        <header className="page-heading">
          <h1>Impostazioni generali</h1>
          <p>Preferenze valide per tutta l'applicazione e per tutti i progetti</p>
        </header>

        <section className="settings-card general-card">
          <h2>Applicazione</h2>
          <p>Configura il comportamento predefinito di Mapi RAG.</p>
          <div className="settings-card-divider" />
          <div className="settings-row">
            <div><strong>Modello predefinito</strong><span>Utilizzato nelle nuove conversazioni</span></div>
            <button className="value-control" type="button">Mapi RAG</button>
          </div>
          <div className="settings-row">
            <strong>Lingua predefinita</strong>
            <span>Italiano</span>
          </div>
        </section>

        <section className="settings-card general-card review-setting">
          <div>
            <h2>Revisione e provenienza</h2>
            <p>Regole applicate alla generazione dei documenti.</p>
          </div>
          <div className="settings-card-divider" />
          <div className="settings-row">
            <strong>Richiedi conferma umana prima dell'esportazione</strong>
            <button
              type="button"
              role="switch"
              aria-checked={reviewRequired}
              className={`toggle${reviewRequired ? ' is-on' : ''}`}
              onClick={() => setReviewRequired((value) => !value)}
            >
              <span />
            </button>
          </div>
        </section>
      </div>
    </AppShell>
  )
}
