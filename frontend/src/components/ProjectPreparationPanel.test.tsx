import { cleanup, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it } from 'vitest'
import type { ProjectDetail } from '../types'
import { ProjectPreparationPanel } from './ProjectPreparationPanel'

const project = { id: 'progetto-test' } as ProjectDetail

describe('ProjectPreparationPanel', () => {
  afterEach(cleanup)
  it('opens documents in the project workspace', () => {
    render(<MemoryRouter><ProjectPreparationPanel project={project} /></MemoryRouter>)
    expect(screen.getByRole('heading', { name: 'Preparazione candidatura' })).toBeVisible()
    expect(screen.getByRole('link', { name: /Moduli e bozze/ })).toHaveAttribute(
      'href', '/projects/progetto-test?documents=docx',
    )
    expect(screen.queryByRole('link', { name: /Template/ })).not.toBeInTheDocument()
  })
  it('preserves the conversation and existing query parameters', () => {
    render(<MemoryRouter initialEntries={['/projects/progetto-test/conversations/chat-1?keep=1']}>
      <ProjectPreparationPanel project={project} />
    </MemoryRouter>)
    expect(screen.getByRole('link', { name: /Moduli e bozze/ })).toHaveAttribute(
      'href', '/projects/progetto-test/conversations/chat-1?keep=1&documents=docx',
    )
  })
})
