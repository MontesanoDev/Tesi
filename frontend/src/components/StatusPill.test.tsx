import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { StatusPill } from './StatusPill'

describe('StatusPill', () => {
  it('renders the requested tone and label', () => {
    render(<StatusPill tone="warning">Da verificare</StatusPill>)

    const badge = screen.getByText('Da verificare')
    expect(badge).toHaveClass('status-pill--warning')
  })
})
