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
      </div>
    </AppShell>
  )
}
