import {
  Database,
  FileText,
  Folder,
  PanelLeft,
  Settings,
  X,
} from 'lucide-react'
import { useState, type ReactNode } from 'react'
import { Link, NavLink } from 'react-router-dom'
import type { ProjectDetail } from '../types'

interface AppShellProps {
  children: ReactNode
  active: 'projects' | 'documents' | 'company' | 'settings'
  project?: ProjectDetail | null
  contentClassName?: string
  shellClassName?: string
}

const navClass = ({ isActive }: { isActive: boolean }) =>
  `rail-button${isActive ? ' rail-button--active' : ''}`

export function AppShell({
  children,
  active,
  project,
  contentClassName = '',
  shellClassName = '',
}: AppShellProps) {
  const [drawerOpen, setDrawerOpen] = useState(false)

  return (
    <div className={`app-shell ${shellClassName}`}>
      <aside className="icon-rail" aria-label="Navigazione principale">
        <button
          className="rail-button rail-button--panel"
          type="button"
          aria-label="Espandi barra laterale"
          title="Espandi barra laterale"
          onClick={() => setDrawerOpen(true)}
        >
          <PanelLeft size={18} />
        </button>
        <NavLink
          className={navClass}
          to="/projects"
          aria-label="Progetti"
          title="Progetti"
        >
          <Folder size={18} />
        </NavLink>
        <Link
          className={`rail-button${active === 'company' ? ' rail-button--active' : ''}`}
          to="/company-knowledge"
          aria-label="Dati aziendali"
          title="Dati aziendali"
        >
          <Database size={18} />
        </Link>
        <NavLink
          className={({ isActive }) => `${navClass({ isActive })} rail-settings`}
          to="/settings"
          aria-label="Impostazioni generali"
          title="Impostazioni generali"
        >
          <Settings size={18} />
        </NavLink>
        <div className="profile-avatar" aria-label="Profilo Mapi Ingegneria">
          M
        </div>
      </aside>

      <main className={`app-content ${contentClassName}`}>{children}</main>

      {drawerOpen && (
        <div className="drawer-layer">
          <button
            className="drawer-scrim"
            type="button"
            aria-label="Chiudi barra laterale"
            onClick={() => setDrawerOpen(false)}
          />
          <aside className="side-drawer" aria-label="Navigazione estesa">
            <div className="drawer-brand">
              <button
                className="icon-button"
                type="button"
                aria-label="Riduci barra laterale"
                title="Riduci barra laterale"
                onClick={() => setDrawerOpen(false)}
              >
                <PanelLeft size={18} />
              </button>
              <div>
                <strong>Mapi RAG</strong>
                <span>Area di progetto</span>
              </div>
              <button
                className="drawer-close"
                type="button"
                aria-label="Chiudi"
                onClick={() => setDrawerOpen(false)}
              >
                <X size={18} />
              </button>
            </div>
            <span className="drawer-label">Navigazione</span>
            <NavLink className="drawer-link" to="/projects">
              <Folder size={18} /> Progetti
            </NavLink>
            <div className="drawer-divider" />
            <span className="drawer-label">Base di conoscenza</span>
            <Link className="knowledge-link" to="/company-knowledge">
              <Database size={18} />
              <span>
                <strong>Dati aziendali</strong>
                <small>Mapi Ingegneria</small>
              </span>
              <em>Globale</em>
            </Link>
            {project && (
              <Link className="knowledge-link" to={`/projects/${project.id}`}>
                <FileText size={18} />
                <span>
                  <strong>Dati del bando</strong>
                  <small>{project.title}</small>
                </span>
                <em className="project-scope">Progetto</em>
              </Link>
            )}
            <div className="drawer-spacer" />
            <NavLink className="drawer-link" to="/settings">
              <Settings size={18} /> Impostazioni
            </NavLink>
            <div className="drawer-profile">
              <span>M</span>
              <div>
                <strong>Mapi Ingegneria</strong>
                <small>Area di lavoro tesi</small>
              </div>
            </div>
          </aside>
        </div>
      )}
    </div>
  )
}
