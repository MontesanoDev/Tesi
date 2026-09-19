import { afterEach, describe, expect, it, vi } from 'vitest'
import { api } from './api'

describe('API errors', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('formats FastAPI validation details without object coercion', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({
        detail: [
          {
            loc: ['body', 'title'],
            msg: 'Il testo deve contenere almeno 3 caratteri',
          },
        ],
      }),
      { status: 422, headers: { 'Content-Type': 'application/json' } },
    )))

    await expect(api.createProject({ title: 'A', description: '' })).rejects.toThrow(
      'title: Il testo deve contenere almeno 3 caratteri',
    )
  })

  it('uses a stable fallback for an unknown error object', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(
      JSON.stringify({ detail: { unexpected: true } }),
      { status: 400, headers: { 'Content-Type': 'application/json' } },
    )))

    await expect(api.projects()).rejects.toThrow('Richiesta non riuscita (400)')
  })

  it('sends DOCX compilation as multipart without forcing a JSON content type', async () => {
    const fetch = vi.fn().mockResolvedValue(new Response(JSON.stringify({ id: 'run-1' }), { status: 201 }))
    vi.stubGlobal('fetch', fetch)
    const file = new File(['docx'], 'modello.docx')
    await api.compileDocument('project-1', file, 'Partecipazione singola')
    const [url, init] = fetch.mock.calls[0]
    expect(url).toBe('/api/projects/project-1/document-compilations')
    expect(init.method).toBe('POST')
    expect(init.body.get('file')).toBe(file)
    expect(init.body.get('instructions')).toBe('Partecipazione singola')
    expect(init.headers.has('Content-Type')).toBe(false)
  })

  it('downloads compilation bytes and handles JSON error responses as errors', async () => {
    const fetch = vi.fn().mockResolvedValueOnce(new Response('docx-bytes'))
      .mockResolvedValueOnce(new Response(JSON.stringify({ detail: 'File non trovato' }), { status: 404 }))
    vi.stubGlobal('fetch', fetch)
    const file = await api.downloadCompilation('project-1', 'run-1', 'docx')
    expect(await file.text()).toBe('docx-bytes')
    expect(fetch.mock.calls[0][0]).toBe('/api/projects/project-1/document-compilations/run-1/download/docx')
    await expect(api.downloadCompilation('project-1', 'run-1', 'report')).rejects.toThrow('File non trovato')
  })
})
