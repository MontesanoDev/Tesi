import { cleanup, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it } from 'vitest'
import type { ProjectDetail } from '../types'
import { ProjectKnowledgeSummary } from './ProjectKnowledgeSummary'

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
  call_fact_count: 0,
  missing_fact_count: 0,
  files: [],
  knowledge_sources: [
    {
      id: 1,
      name: 'Dati estratti dal bando',
      detail: 'Call Facts verificati',
      scope: 'project',
      tone: 'success',
      item_count: 4,
    },
    {
      id: 2,
      name: 'Modelli',
      detail: 'Voce legacy da non mostrare',
      scope: 'project',
      tone: 'purple',
      item_count: 3,
    },
    {
      id: -1,
      name: 'Company KB',
      detail: '3 frammenti disponibili',
      scope: 'global',
      tone: 'success',
      item_count: 2,
    },
  ],
  conversations: [],
}

describe('ProjectKnowledgeSummary', () => {
  afterEach(cleanup)

  it('shows only the three knowledge channels with stable empty states', () => {
    render(<ProjectKnowledgeSummary project={project} />)

    expect(screen.getByRole('heading', { name: 'Conoscenza utilizzata' })).toBeVisible()
    expect(screen.getByText('Call Facts')).toBeVisible()
    expect(screen.getByText('4 verificati')).toBeVisible()
    expect(screen.getByText('Company KB')).toBeVisible()
    expect(screen.getByText('2 documenti')).toBeVisible()
    expect(screen.getByText('General KB')).toBeVisible()
    expect(screen.getByText('0 documenti')).toBeVisible()
    expect(screen.queryByText('Modelli')).toBeNull()
  })
})
