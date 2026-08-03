import { Plus } from 'lucide-react'
import { StatusPill } from './StatusPill'
import type { ProjectDetail } from '../types'

export function ProjectKnowledgePanel({ project }: { project: ProjectDetail }) {
  return (
    <aside className="knowledge-panel">
      <section className="knowledge-section knowledge-instructions">
        <div className="panel-title-row">
          <h2>Istruzioni</h2>
          <button className="icon-button" type="button" aria-label="Modifica istruzioni">
            <Plus size={18} />
          </button>
        </div>
        <p>{project.instructions}</p>
      </section>

      <section className="knowledge-section knowledge-files">
        <div className="panel-title-row">
          <h2>File e fonti</h2>
          <button className="icon-button" type="button" aria-label="Aggiungi file">
            <Plus size={18} />
          </button>
        </div>
        <div className="file-list">
          {project.files.length === 0 ? (
            <p className="empty-list">Nessun file collegato</p>
          ) : (
            project.files.map((file) => (
              <div className="file-row" key={file.id}>
                <div>
                  <strong>{file.name}</strong>
                  <span>{file.metadata}</span>
                </div>
                <StatusPill tone={file.kind === 'template' ? 'purple' : 'success'}>
                  {file.status}
                </StatusPill>
              </div>
            ))
          )}
        </div>
      </section>

      <section className="knowledge-section knowledge-summary">
        <h2>Conoscenza collegata</h2>
        <div className="knowledge-source-list">
          {project.knowledge_sources.map((source) => (
            <div className="knowledge-source" key={source.id}>
              <span className={`source-dot source-dot--${source.tone}`} />
              <strong>{source.name}</strong>
              <span>
                {source.item_count}{' '}
                {source.name === 'Modelli' ? 'disponibili' : 'verificati'}
              </span>
            </div>
          ))}
        </div>
        <p className="scope-note">Le fonti restano limitate a questo progetto.</p>
      </section>
    </aside>
  )
}
