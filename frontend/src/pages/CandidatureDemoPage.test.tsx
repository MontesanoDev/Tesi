import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { CandidatureDemoPage } from './CandidatureDemoPage'
import { facsimileHtml } from './candidatureDemo'

function renderDemo() {
  return render(<MemoryRouter><CandidatureDemoPage /></MemoryRouter>)
}

function openReview() {
  fireEvent.click(screen.getByRole('button', { name: 'Usa modello dimostrativo' }))
  fireEvent.click(screen.getByRole('button', { name: 'Simula compilazione' }))
  fireEvent.click(screen.getByRole('button', { name: 'Revisiona bozza' }))
}

describe('CandidatureDemoPage', () => {
  afterEach(() => { cleanup(); vi.unstubAllGlobals(); vi.restoreAllMocks() })

  it('requires a model and completes the simulation without API calls', () => {
    const fetch = vi.fn()
    vi.stubGlobal('fetch', fetch)
    renderDemo()
    expect(screen.getByText('Demo concettuale')).toBeVisible()
    expect(screen.getByRole('button', { name: 'Simula compilazione' })).toBeDisabled()
    openReview()
    expect(screen.getByRole('status')).toHaveTextContent('2 dati da completare')
    expect(screen.getByLabelText('Ente proponente')).toHaveValue('Comune di Valleverde')
    expect(screen.getByRole('button', { name: "Vai all'esportazione" })).toBeDisabled()

    fireEvent.change(screen.getByLabelText('Responsabile del procedimento'), { target: { value: 'Referente demo' } })
    fireEvent.change(screen.getByLabelText('Importo richiesto (EUR)'), { target: { value: '450000' } })
    fireEvent.click(screen.getByLabelText('Ho controllato i dati del facsimile'))
    fireEvent.click(screen.getByRole('button', { name: "Vai all'esportazione" }))
    expect(screen.getByRole('button', { name: 'Scarica facsimile HTML' })).toBeEnabled()
    expect(screen.getByText(/La compilazione del modello originale resta da implementare/)).toBeVisible()
    expect(fetch).not.toHaveBeenCalled()
  })

  it('invalidates confirmation after editing and prevents export with invalid data', () => {
    renderDemo()
    openReview()
    fireEvent.change(screen.getByLabelText('Responsabile del procedimento'), { target: { value: 'Referente demo' } })
    fireEvent.change(screen.getByLabelText('Importo richiesto (EUR)'), { target: { value: '1000' } })
    fireEvent.click(screen.getByLabelText('Ho controllato i dati del facsimile'))
    expect(screen.getByRole('button', { name: "Vai all'esportazione" })).toBeEnabled()
    fireEvent.change(screen.getByLabelText('Importo richiesto (EUR)'), { target: { value: '-1' } })
    expect(screen.getByLabelText('Ho controllato i dati del facsimile')).not.toBeChecked()
    fireEvent.click(screen.getByLabelText('Ho controllato i dati del facsimile'))
    expect(screen.getByRole('button', { name: "Vai all'esportazione" })).toBeDisabled()
  })

  it('rejects unsupported or empty files without sending them anywhere', () => {
    renderDemo()
    const input = screen.getByLabelText('Seleziona modello dimostrativo')
    fireEvent.change(input, { target: { files: [new File(['testo'], 'nota.txt')] } })
    expect(screen.getByRole('alert')).toHaveTextContent('PDF o DOCX')
    fireEvent.change(input, { target: { files: [new File([], 'vuoto.pdf')] } })
    expect(screen.getByRole('alert')).toHaveTextContent('non vuoto')
    fireEvent.change(input, { target: { files: [new File(['demo'], 'modello.pdf')] } })
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
    expect(screen.getByText('modello.pdf')).toBeVisible()
    expect(screen.getByText(/Il file non viene letto o conservato/)).toBeVisible()
  })

  it('resets all simulated data when restarting', () => {
    renderDemo()
    openReview()
    fireEvent.click(screen.getByRole('button', { name: 'Ricomincia demo' }))
    expect(screen.getByRole('button', { name: 'Simula compilazione' })).toBeDisabled()
    expect(screen.queryByText('Comune di Valleverde')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: /Esportazione/ })).toBeDisabled()
  })

  it('exports a clearly marked HTML facsimile and escapes entered content', () => {
    const html = facsimileHtml({
      ente: '<img src=x onerror=alert(1)>', intervento: 'Intervento demo', supporto: 'Mapi',
      responsabile: 'Referente demo', importo: '12500.50',
    })
    const result = new DOMParser().parseFromString(html, 'text/html')
    expect(result.querySelector('img')).toBeNull()
    expect(result.body.textContent).toContain('<img src=x onerror=alert(1)>')
    expect(result.body.textContent).toContain('NON UTILIZZABILE PER INVII UFFICIALI')
    expect(result.body.textContent).toContain('12.500,50')
  })
})
