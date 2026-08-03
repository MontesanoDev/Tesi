import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { ProjectDetail } from '../types'
import { ProjectKnowledgePanel } from './ProjectKnowledgePanel'

vi.mock('../api', () => ({
  api: {
    uploadProjectFile: vi.fn(),
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
  instructions: 'Usa soltanto le fonti.',
  call_fact_count: 0,
  missing_fact_count: 0,
  files: [],
  knowledge_sources: [],
  conversations: [],
}

describe('ProjectKnowledgePanel', () => {
  beforeEach(() => {
    vi.mocked(api.uploadProjectFile).mockReset()
  })

  it('uploads a source and refreshes the project', async () => {
    const onProjectChange = vi.fn().mockResolvedValue(undefined)
    vi.mocked(api.uploadProjectFile).mockResolvedValue({
      id: 3,
      name: 'capitolato.txt',
      metadata: 'TXT · 1 KB · 2 frammenti',
      kind: 'source',
      status: 'Indicizzato',
      page_count: 1,
      chunk_count: 2,
    })
    render(
      <ProjectKnowledgePanel project={project} onProjectChange={onProjectChange} />,
    )

    const input = screen.getByLabelText('Seleziona un documento da indicizzare')
    const file = new File(['contenuto tecnico'], 'capitolato.txt', {
      type: 'text/plain',
    })
    fireEvent.change(input, { target: { files: [file] } })

    await waitFor(() => {
      expect(api.uploadProjectFile).toHaveBeenCalledWith(project.id, file)
      expect(onProjectChange).toHaveBeenCalledOnce()
    })
    expect(
      screen.getByText('capitolato.txt indicizzato in 2 frammenti.'),
    ).toBeVisible()
  })
})
