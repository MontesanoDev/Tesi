import { Link } from 'react-router-dom'
import { AppShell } from '../components/AppShell'
import { AiSettingsPanel } from '../components/AiSettingsPanel'

export function GeneralSettingsPage() {
  return (
    <AppShell active="settings">
      <Link className="back-link" to="/projects">← Tutti i progetti</Link>
      <div className="settings-page page-container">
        <header className="page-heading">
          <h1>Impostazioni generali</h1>
          <p>Preferenze valide per tutta l'applicazione e per tutti i progetti</p>
        </header>

        <AiSettingsPanel />
        <section className="settings-card general-card">
          <h2>Applicazione</h2>
          <p>Configura il comportamento predefinito di Mapi RAG.</p>
          <div className="settings-card-divider" />
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
            <p>I documenti generati sono bozze: verifica dati, campi e dichiarazioni prima di usarli.</p>
          </div>
        </section>
      </div>
    </AppShell>
  )
}
