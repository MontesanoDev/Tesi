import { LoaderCircle, Plus } from 'lucide-react'
import { useRef, useState, type ChangeEvent } from 'react'
import { api } from '../api'
import { StatusPill } from './StatusPill'
import type { ProjectDetail } from '../types'

interface ProjectKnowledgePanelProps {
  project: ProjectDetail
  onProjectChange: () => Promise<void>
}

export function ProjectKnowledgePanel({
  project,
  onProjectChange,
}: ProjectKnowledgePanelProps) {
  const fileInput = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadMessage, setUploadMessage] = useState<string | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)

  async function uploadFile(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0]
    event.target.value = ''
    if (!file) return

    setUploading(true)
    setUploadMessage(null)
    setUploadError(null)
    try {
      const uploaded = await api.uploadProjectFile(project.id, file)
      await onProjectChange()
      setUploadMessage(
        `${uploaded.name} indicizzato in ${uploaded.chunk_count} ${uploaded.chunk_count === 1 ? 'frammento' : 'frammenti'}.`,
      )
    } catch (reason) {
      setUploadError(reason instanceof Error ? reason.message : 'Caricamento non riuscito')
    } finally {
      setUploading(false)
    }
  }

  return (
    <aside className="knowledge-panel">
      <input
        ref={fileInput}
        className="source-file-input"
        type="file"
        aria-label="Seleziona un documento da indicizzare"
        accept=".pdf,.txt,application/pdf,text/plain"
        onChange={uploadFile}
      />
      <section className="knowledge-section knowledge-files">
        <div className="panel-title-row">
          <h2>File e fonti</h2>
          <button
            className="icon-button"
            type="button"
            aria-label="Aggiungi file"
            title="Aggiungi un documento PDF o TXT"
            disabled={uploading}
            onClick={() => fileInput.current?.click()}
          >
            {uploading ? <LoaderCircle className="spin" size={18} /> : <Plus size={18} />}
          </button>
        </div>
        {uploading && <p className="upload-feedback">Estrazione e indicizzazione in corso...</p>}
        {uploadMessage && <p className="upload-feedback upload-feedback--success">{uploadMessage}</p>}
        {uploadError && <p className="upload-feedback upload-feedback--error" role="alert">{uploadError}</p>}
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
                {source.name === 'Modelli'
                  ? 'disponibili'
                  : source.name === 'Company KB' || source.name === 'General KB'
                    ? 'documenti'
                    : 'verificati'}
              </span>
            </div>
          ))}
        </div>
        <p className="scope-note">Le fonti restano limitate a questo progetto.</p>
      </section>
    </aside>
  )
}
