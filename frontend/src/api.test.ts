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
})
