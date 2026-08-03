import { useState } from 'react'
import { Link } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { StatusPill } from '../components/StatusPill'

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

        <section className="settings-card general-card">
          <h2>Conoscenza globale</h2>
          <p>Fonti condivise e dati aziendali disponibili in tutti i progetti.</p>
          <div className="settings-card-divider" />
          <div className="linked-source-grid">
            <div className="linked-source linked-source--status">
              <div><strong>General KB</strong><span>Norme e materiali tecnici</span></div>
              <StatusPill tone="info">12 fonti</StatusPill>
            </div>
            <div className="linked-source linked-source--status">
              <div><strong>Company Facts</strong><span>Mapi Ingegneria S.r.l.</span></div>
              <StatusPill tone="success">28 verificati</StatusPill>
            </div>
          </div>
          <div className="settings-actions">
            <button className="button button--compact" type="button">Gestisci conoscenza globale</button>
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
