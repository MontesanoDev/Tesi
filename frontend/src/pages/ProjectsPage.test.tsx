import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import type { ProjectSummary } from '../types'
import { ProjectsPage } from './ProjectsPage'

vi.mock('../api', () => ({ api: { projects: vi.fn() } }))

const projects: ProjectSummary[] = [
  { id: 'zeta', title: 'Zeta', description: 'Intervento scuola' },
  { id: 'dieci', title: 'progetto 10', description: 'Rete idrica' },
  { id: 'due', title: 'Progetto 2', description: 'Rete idrica' },
  { id: 'alfa', title: 'Alfa', description: 'Intervento scuola' },
].map((item) => ({ ...item, status: 'Bozza', status_tone: 'warning',
  updated_label: 'Aggiornato ora', source_count: 0, model_count: 0,
}))

function cardTitles() {
  return Array.from(document.querySelectorAll('.project-card strong'), (element) => element.textContent)
}

async function setup() {
  render(<MemoryRouter><ProjectsPage /></MemoryRouter>)
  await waitFor(() => expect(cardTitles()).toHaveLength(projects.length))
}

describe('ProjectsPage sorting', () => {
  afterEach(cleanup)
  beforeEach(() => vi.mocked(api.projects).mockReset().mockResolvedValue(projects))

  it('defaults to the API modification order and restores it after sorting by name', async () => {
    await setup()
    expect(screen.getByRole('combobox', { name: 'Ordina progetti' })).toHaveValue('updated')
    expect(cardTitles()).toEqual(['Zeta', 'progetto 10', 'Progetto 2', 'Alfa'])
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'name' } })
    expect(cardTitles()).toEqual(['Alfa', 'Progetto 2', 'progetto 10', 'Zeta'])
    expect(projects.map((item) => item.title)).toEqual(['Zeta', 'progetto 10', 'Progetto 2', 'Alfa'])
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'updated' } })
    expect(cardTitles()).toEqual(['Zeta', 'progetto 10', 'Progetto 2', 'Alfa'])
    expect(api.projects).toHaveBeenCalledTimes(1)
  })

  it('combines sorting and filtering without losing the selected order', async () => {
    await setup()
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'name' } })
    fireEvent.change(screen.getByLabelText('Cerca progetti'), { target: { value: 'scuola' } })
    expect(cardTitles()).toEqual(['Alfa', 'Zeta'])
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'updated' } })
    expect(cardTitles()).toEqual(['Zeta', 'Alfa'])
    fireEvent.change(screen.getByLabelText('Cerca progetti'), { target: { value: 'inesistente' } })
    expect(cardTitles()).toEqual([])
    fireEvent.change(screen.getByRole('combobox'), { target: { value: 'name' } })
    fireEvent.change(screen.getByLabelText('Cerca progetti'), { target: { value: '' } })
    expect(cardTitles()).toEqual(['Alfa', 'Progetto 2', 'progetto 10', 'Zeta'])
  })
})
