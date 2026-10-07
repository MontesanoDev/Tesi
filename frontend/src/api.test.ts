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

  it('sends structured mentions, conversation scope and versioned session actions', async () => {
    const fetch = vi.fn().mockImplementation(async () => new Response('{}', { status: 200 }))
    vi.stubGlobal('fetch', fetch)
    await api.projectAnswer('alpha', 'riassumilo', 'chat', undefined, 42)
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ question: 'riassumilo', conversation_id: 'chat', form_id: 42 })
    await api.startCompilationSession('alpha', 42, 'chat')
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({ form_id: 42, conversation_id: 'chat', start_in_chat: true })
    await api.compilationSessions('alpha', 'chat/with space')
    expect(new URL(fetch.mock.calls[2][0], 'http://test').searchParams.get('conversation_id')).toBe('chat/with space')
    await api.resolveCompilationSession('alpha', 'session', 3)
    expect(JSON.parse(fetch.mock.calls[3][1].body)).toEqual({ version: 3 })
    await api.updateCompilationFields('alpha', 'session', 5, [{ field_id: 't1.r1.c1', action: 'set', value: 'Dato' }])
    expect(fetch.mock.calls[4][1].method).toBe('PATCH')
    expect(JSON.parse(fetch.mock.calls[4][1].body)).toEqual({ version: 5, fields: [{ field_id: 't1.r1.c1', action: 'set', value: 'Dato' }] })
    await api.finalizeCompilationSession('alpha', 'session', 6, false)
    expect(JSON.parse(fetch.mock.calls[5][1].body)).toEqual({ version: 6, allow_unresolved: false })
  })

  it('exposes field validation messages returned by the existing backend', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(new Response(JSON.stringify({
      detail: { field_id: 't1.r1.c1', errors: ['Email non valida', 'Valore non ammesso'] },
    }), { status: 422 })))
    await expect(api.updateCompilationFields('alpha', 'session', 3, []))
      .rejects.toThrow('Email non valida; Valore non ammesso')
  })

  it('sends the displayed question revision and requests budgeted automatic steps', async () => {
    const fetch = vi.fn().mockImplementation(async () => new Response('{}'))
    vi.stubGlobal('fetch', fetch)
    await api.projectAnswer('alpha', '12 giugno 2014', 'chat', undefined, 42,
      { session_id: 'session', version: 5 })
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ question: '12 giugno 2014',
      conversation_id: 'chat', form_id: 42, compilation_session_id: 'session', compilation_version: 5 })
    await api.resolveCompilationSession('alpha', 'session', 5, undefined, undefined, true)
    expect(JSON.parse(fetch.mock.calls[1][1].body)).toEqual({ version: 5, automatic: true })
  })

})
