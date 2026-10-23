import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { readChatDraft, saveChatDraft } from './chatMessageRecovery'

describe('Copia di recupero confinata alla scheda e alla conversazione', () => {
  beforeEach(() => sessionStorage.clear())
  afterEach(() => vi.restoreAllMocks())

  it('conserva testo e riferimento documento esatti, senza tagli', () => {
    const message = { text: '  È una risposta\n' + '😀'.repeat(5000) + '  ',
      document_reference: { document_id: 7, name: 'modulo.docx', role: 'form' as const } }
    expect(saveChatDraft('alfa', 'c1', message)).toBe(true)
    expect(readChatDraft('alfa', 'c1')).toEqual({ message, unavailable: false })
    expect(readChatDraft('beta', 'c1').message).toBeNull()
    expect(readChatDraft('alfa', 'c2').message).toBeNull()
  })

  it('non crea collisioni fra ID che contengono separatori', () => {
    const one = { text: 'Primo', document_reference: null }
    const two = { text: 'Secondo', document_reference: null }
    saveChatDraft('alfa:beta', 'c1', one)
    saveChatDraft('alfa', 'beta:c1', two)
    expect(readChatDraft('alfa:beta', 'c1').message).toEqual(one)
    expect(readChatDraft('alfa', 'beta:c1').message).toEqual(two)
  })

  it('rende osservabile l’indisponibilità dello storage senza simulare un salvataggio', () => {
    vi.spyOn(Storage.prototype, 'setItem').mockImplementation(() => { throw new DOMException('Quota') })
    expect(saveChatDraft('alfa', null, { text: 'Originale', document_reference: null })).toBe(false)
    vi.spyOn(Storage.prototype, 'getItem').mockImplementation(() => { throw new DOMException('Denied') })
    expect(readChatDraft('alfa', null)).toEqual({ message: null, unavailable: true })
  })

  it.each(['broken JSON', '{"text":3}', '{"text":"Originale","document_reference":{"role":"admin"}}'])(
    'rifiuta copie corrotte senza inviare dati: %s', (raw) => {
      sessionStorage.setItem('mapi:chat-draft:alfa:c1', raw)
      expect(readChatDraft('alfa', 'c1')).toEqual({ message: null, unavailable: true })
    },
  )
})
