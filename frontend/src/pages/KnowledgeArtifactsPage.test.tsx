import { cleanup, render, screen } from '@testing-library/react'
import { createMemoryRouter, RouterProvider } from 'react-router-dom'
import { afterEach, describe, expect, it } from 'vitest'
import { KnowledgeArtifactsPage } from './KnowledgeArtifactsPage'

describe('legacy document navigation', () => {
  afterEach(cleanup)
  it.each(['', '?artifact=template', '?artifact=output_draft'])('redirects %s to the project', async (query) => {
    const router = createMemoryRouter([
      { path: '/projects/:projectId/knowledge', element: <KnowledgeArtifactsPage /> },
      { path: '/projects/:projectId', element: <div>Chat progetto</div> },
    ], { initialEntries: [`/projects/primo/knowledge${query}`] })
    render(<RouterProvider router={router} />)
    expect(await screen.findByText('Chat progetto')).toBeVisible()
    expect(router.state.location.pathname).toBe('/projects/primo')
    expect(router.state.location.search).toBe('')
  })
})
