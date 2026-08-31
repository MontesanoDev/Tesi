import { cleanup, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { ProjectDetail } from '../types'
import { ProjectPreparationPanel } from './ProjectPreparationPanel'

vi.mock('../api', () => ({
  api: {
    projectArtifacts: vi.fn(),
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

  it('links each preparation step to its artifact and shows live status', async () => {
    render(
      <MemoryRouter>
        <ProjectPreparationPanel project={project} />
      </MemoryRouter>,
    )

    expect(screen.getByRole('heading', { name: 'Preparazione candidatura' })).toBeVisible()
    expect(screen.getByRole('link', { name: /Call Facts/ })).toHaveAttribute(
      'href',
      '/projects/progetto-test/knowledge?artifact=call_facts',
    )
    expect(screen.getByRole('link', { name: /Dati del progetto/ })).toHaveAttribute(
      'href',
      '/projects/progetto-test/knowledge?artifact=project_facts',
    )
    expect(screen.getByRole('link', { name: /Template/ })).toHaveAttribute(
      'href',
      '/projects/progetto-test/knowledge?artifact=template',
    )
    expect(screen.getByRole('link', { name: /Draft/ })).toHaveAttribute(
      'href',
      '/projects/progetto-test/knowledge?artifact=output_draft',
    )
    await waitFor(() => {
      expect(screen.getByRole('link', { name: /Call Facts/ })).toHaveTextContent('Da verificare')
      expect(screen.getByRole('link', { name: /Template/ })).toHaveTextContent('Versione 2')
    })
  })
})
