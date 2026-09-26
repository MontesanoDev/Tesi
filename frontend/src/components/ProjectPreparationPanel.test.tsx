import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { ProjectDetail } from '../types'
import { ProjectPreparationPanel } from './ProjectPreparationPanel'

vi.mock('../api', () => ({
  api: {
    projectArtifacts: vi.fn(),
    documentCompilations: vi.fn(),
  },
}))

const project: ProjectDetail = {
  id: 'progetto-test',
  title: 'Progetto test',
  description: 'Descrizione',
  status: 'In analisi',
  status_tone: 'info',
  updated_label: 'Aggiornato ora',
  source_count: 0,
  model_count: 0,
  instructions: '',
  call_fact_count: 4,
  missing_fact_count: 1,
  files: [],
  knowledge_sources: [],
  conversations: [],
}

describe('ProjectPreparationPanel', () => {
  afterEach(cleanup)

  beforeEach(() => {
    vi.mocked(api.documentCompilations).mockReset().mockResolvedValue([])
    vi.mocked(api.projectArtifacts).mockReset()
    vi.mocked(api.projectArtifacts).mockResolvedValue([
      {
        id: 'progetto-test--call-facts',
        kind: 'call_facts',
        scope: 'project',
        title: 'Call Facts',
        filename: 'call-facts.md',
        status: 'Da verificare',
        byte_size: 120,
        version: 3,
        updated_at: '2026-08-31 10:00:00',
        editable: true,
        chunk_count: 1,
      },
      {
        id: 'progetto-test--template',
        kind: 'template',
        scope: 'project',
        title: 'Template',
        filename: 'template.md',
        status: 'Bozza',
        byte_size: 80,
        version: 2,
        updated_at: '2026-08-31 10:00:00',
        editable: true,
        chunk_count: 1,
      },
    ])
  })

  it('links directly to Template with its live status and no project data step', async () => {
    render(
      <MemoryRouter>
        <ProjectPreparationPanel project={project} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Preparazione candidatura' })).toBeVisible()
    expect(screen.queryByRole('link', { name: /Call Facts/ })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Dati del progetto/ })).not.toBeInTheDocument()
    expect(screen.getByRole('link', { name: /Template/ })).toHaveAttribute(
      'href',
      '/projects/progetto-test/knowledge?artifact=template',
    )
    expect(screen.queryByRole('link', { name: /Draft/ })).not.toBeInTheDocument()
    expect(screen.getAllByRole('link')).toHaveLength(1)
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Template/ })).toHaveTextContent('Versione 2')
    })
  })

  it('shows the saved compilation status under Template', async () => {
    const artifacts = await api.projectArtifacts(project.id)
    vi.mocked(api.projectArtifacts).mockResolvedValue([...artifacts, {
      ...artifacts[1], id: 'progetto-test--draft', kind: 'output_draft',
      title: 'Draft', filename: 'draft.md', status: 'Da verificare', version: 4,
    }])
    render(<MemoryRouter><ProjectPreparationPanel project={project} /></MemoryRouter>)
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Template/ })).toHaveTextContent('Compilazione v4')
      expect(screen.getByRole('link', { name: /Template/ })).toHaveTextContent('Da verificare')
    })
    expect(screen.queryByRole('link', { name: /Draft/ })).not.toBeInTheDocument()
  })

  it('shows persisted Word compilations ahead of the legacy text status', async () => {
    vi.mocked(api.documentCompilations).mockResolvedValue([{
      id: 'run-1', project_id: project.id, template_name: 'domanda.docx',
      created_at: '2026-09-15T13:00:00Z', status: 'needs_review',
      downloads: { docx: '', report: '', template: '' },
    }])
    render(<MemoryRouter><ProjectPreparationPanel project={project} /></MemoryRouter>)
    await waitFor(() => expect(screen.getByRole('link', { name: /Template/ })).toHaveTextContent('1 compilazione Word'))
    expect(screen.getByRole('link', { name: /Template/ })).toHaveTextContent('Da verificare')
  })
})
