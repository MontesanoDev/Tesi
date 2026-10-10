import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { api } from '../api'
import providerCatalog from '../../e2e/ai-providers.fixture.json'
import type { AiProfile, AiProviderDefinition, ProjectAiSelection } from '../types'
import { AiSettingsPanel } from './AiSettingsPanel'
import { ProjectModelSelector } from './ProjectModelSelector'

vi.mock('../api', () => ({ api: {
  aiSettings: vi.fn(), saveAiProfile: vi.fn(), deleteAiProfile: vi.fn(),
  setDefaultAiProfile: vi.fn(), checkAiConnection: vi.fn(),
  projectAiModel: vi.fn(), setProjectAiModel: vi.fn(),
  beginOpenRouterLogin: vi.fn(), completeOpenRouterLogin: vi.fn(),
} }))

const cloud: AiProfile = { id: 'cloud', name: 'DeepSeek ufficio', provider: 'deepseek',
  model: 'remote-test', base_url: 'https://provider.test', context_window: 32768, has_api_key: true }
const local: AiProfile = { id: 'local', name: 'Ollama ufficio', provider: 'ollama',
  model: 'local-test', base_url: 'http://127.0.0.1:11434', context_window: 16384, has_api_key: false }
const providers = providerCatalog as AiProviderDefinition[]
const settings = { providers, profiles: [cloud, local], default_profile_id: cloud.id }

beforeEach(() => {
  vi.resetAllMocks()
  vi.mocked(api.aiSettings).mockResolvedValue(settings)
  vi.mocked(api.projectAiModel).mockResolvedValue({ profile_id: null, effective_profile: cloud, thinking: false })
})
afterEach(() => { cleanup(); vi.restoreAllMocks() })

describe('AI settings', () => {
  it('creates a cloud profile and removes the secret from the rendered form after saving', async () => {
    vi.mocked(api.aiSettings).mockResolvedValue({ providers, profiles: [], default_profile_id: null })
    vi.mocked(api.saveAiProfile).mockResolvedValue(cloud)
    render(<AiSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiungi modello' }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Servizio' }), { target: { value: 'deepseek' } })
    fireEvent.change(screen.getByLabelText('Chiave API'), { target: { value: 'only-a-test-secret' } })
    fireEvent.change(screen.getByLabelText('Modello'), { target: { value: 'remote-test' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await screen.findByText('DeepSeek ufficio')
    expect(api.saveAiProfile).toHaveBeenCalledWith(expect.objectContaining({ api_key: 'only-a-test-secret', provider: 'deepseek' }), undefined)
    expect(screen.queryByDisplayValue('only-a-test-secret')).not.toBeInTheDocument()
    expect(screen.getByText('Predefinito')).toBeVisible()
  })

  it('discovers and saves models from the configured remote Ollama endpoint', async () => {
    const remoteUrl = 'https://ollama.example.test'
    vi.mocked(api.checkAiConnection).mockResolvedValue({ models: ['local-test', 'another-model'], message: 'Collegamento riuscito.' })
    vi.mocked(api.saveAiProfile).mockResolvedValue({ ...local, base_url: remoteUrl })
    render(<AiSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiungi modello' }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Servizio' }), { target: { value: 'deepseek' } })
    fireEvent.change(screen.getByLabelText('Servizio'), { target: { value: 'ollama' } })
    expect(screen.getByLabelText(/Indirizzo del servizio/)).toBeVisible()
    fireEvent.change(screen.getByLabelText(/Indirizzo del servizio/), { target: { value: remoteUrl } })
    expect(screen.queryByLabelText('Chiave API')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento e trova modelli' }))
    expect(await screen.findByLabelText('Modello')).toHaveValue('local-test')
    expect(api.checkAiConnection).toHaveBeenCalledWith(expect.objectContaining({ provider: 'ollama', api_key: '', base_url: remoteUrl }))
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await waitFor(() => expect(api.saveAiProfile).toHaveBeenCalledWith(expect.objectContaining({ model: 'local-test', provider: 'ollama', base_url: remoteUrl }), undefined))
  })

  it('preserves the saved key when editing, and reuses it for connection checks', async () => {
    vi.mocked(api.saveAiProfile).mockResolvedValue({ ...cloud, model: 'updated-model' })
    vi.mocked(api.checkAiConnection).mockResolvedValue({ models: ['remote-test'], message: 'Collegamento riuscito.' })
    render(<AiSettingsPanel />)
    await screen.findByText('DeepSeek ufficio')
    fireEvent.click(screen.getAllByRole('button', { name: 'Modifica' })[0])
    expect(screen.getByLabelText(/Chiave API/)).toHaveValue('')
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento e trova modelli' }))
    await screen.findByText('Collegamento riuscito.')
    expect(api.checkAiConnection).toHaveBeenCalledWith(expect.objectContaining({ profile_id: 'cloud', api_key: '', clear_api_key: false }))
    fireEvent.change(screen.getByLabelText('Modello'), { target: { value: 'updated-model' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await waitFor(() => expect(api.saveAiProfile).toHaveBeenCalledWith(expect.objectContaining({ api_key: '', model: 'updated-model' }), 'cloud'))
  })

  it('retains the form and presents connection errors', async () => {
    vi.mocked(api.checkAiConnection).mockRejectedValue(new Error('Servizio non raggiungibile'))
    render(<AiSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiungi modello' }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Servizio' }), { target: { value: 'deepseek' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verifica collegamento e trova modelli' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Servizio non raggiungibile')
    expect(screen.getByRole('button', { name: 'Salva modello' })).toBeEnabled()
    expect(api.saveAiProfile).not.toHaveBeenCalled()
  })

  it('offers the cloud providers with their own endpoints and key links', async () => {
    vi.mocked(api.saveAiProfile).mockResolvedValue({ ...cloud, provider: 'anthropic' })
    render(<AiSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiungi modello' }))
    for (const provider of providers) {
      expect(within(screen.getByRole('combobox', { name: 'Servizio' })).getByRole('option', { name: provider.name })).toHaveValue(provider.id)
    }
    fireEvent.change(screen.getByRole('combobox', { name: 'Servizio' }), { target: { value: 'anthropic' } })
    expect(screen.getByLabelText('Servizio')).toHaveValue('anthropic')
    expect(screen.getByRole('link', { name: /Ottieni una chiave/ })).toHaveAttribute('href', providers[1].credentials_url)
    fireEvent.change(screen.getByLabelText('Chiave API'), { target: { value: 'fake-claude-key' } })
    fireEvent.change(screen.getByLabelText('Modello'), { target: { value: 'claude-test' } })
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await waitFor(() => expect(api.saveAiProfile).toHaveBeenCalledWith(expect.objectContaining({
      provider: 'anthropic', base_url: 'https://api.anthropic.com/v1', api_key: 'fake-claude-key', model: 'claude-test',
    }), undefined))
  })

  it('connects OpenRouter with a temporary token, without receiving its API key', async () => {
    const token = 'temporary-connection-token'
    vi.mocked(api.beginOpenRouterLogin).mockResolvedValue({ connection_token: token,
      authorization_url: 'https://openrouter.ai/auth?code_challenge=test', expires_in: 600 })
    vi.mocked(api.completeOpenRouterLogin).mockResolvedValue({ message: 'Account collegato' })
    vi.mocked(api.checkAiConnection).mockResolvedValue({ models: ['test/model'], message: 'Collegamento riuscito.' })
    vi.mocked(api.saveAiProfile).mockResolvedValue({ ...cloud, id: 'router', name: 'OpenRouter', provider: 'openrouter' })
    render(<AiSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Aggiungi modello' }))
    fireEvent.change(screen.getByRole('combobox', { name: 'Servizio' }), { target: { value: 'openrouter' } })
    fireEvent.click(screen.getByRole('button', { name: 'Accedi con OpenRouter' }))
    expect(await screen.findByRole('link', { name: /Apri accesso/ })).toHaveAttribute('target', '_blank')
    fireEvent.change(screen.getByLabelText('Codice di autorizzazione'), { target: { value: 'one-time-code' } })
    fireEvent.click(screen.getByRole('button', { name: 'Collega account' }))
    await screen.findByText('Account collegato. Scegli il modello e salva.')
    expect(api.completeOpenRouterLogin).toHaveBeenCalledWith(token, 'one-time-code')
    await waitFor(() => expect(screen.getByLabelText('Modello')).toHaveValue('test/model'))
    expect(screen.queryByLabelText('Chiave API')).not.toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Salva modello' }))
    await waitFor(() => expect(api.saveAiProfile).toHaveBeenCalledWith(expect.objectContaining({
      provider: 'openrouter', connection_token: token, api_key: '', model: 'test/model',
    }), undefined))
    expect(screen.queryByDisplayValue('one-time-code')).not.toBeInTheDocument()
  })

  it('updates the default, cancels deletion, then shows a blocked deletion', async () => {
    vi.mocked(api.setDefaultAiProfile).mockResolvedValue({ ...settings, default_profile_id: 'local' })
    vi.mocked(api.deleteAiProfile).mockRejectedValue(new Error('Configurazione selezionata in un progetto'))
    vi.spyOn(window, 'confirm').mockReturnValue(false)
    render(<AiSettingsPanel />)
    fireEvent.click(await screen.findByRole('button', { name: 'Usa come predefinito' }))
    await screen.findByText('Modello predefinito aggiornato.')
    const localRow = screen.getByText('Ollama ufficio').closest('li')!
    expect(within(localRow).getByText('Predefinito')).toBeVisible()
    fireEvent.click(within(localRow).getByRole('button', { name: 'Elimina' }))
    expect(api.deleteAiProfile).not.toHaveBeenCalled()
    vi.mocked(window.confirm).mockReturnValue(true)
    fireEvent.click(within(localRow).getByRole('button', { name: 'Elimina' }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Configurazione selezionata')
    expect(screen.getByText('Ollama ufficio')).toBeVisible()
  })
})

describe('project model selection', () => {
  function setup(disabled = false, onChanging = vi.fn()) {
    return { onChanging, ...render(<MemoryRouter>
      <ProjectModelSelector projectId="project" disabled={disabled} onChanging={onChanging} />
    </MemoryRouter>) }
  }

  async function openMenu() {
    fireEvent.click(screen.getByRole('button', { name: 'Impostazioni AI' }))
    return screen.findByRole('menuitemradio', { name: /Usa predefinito/ })
  }

  it('persists a project override and can return to the global default', async () => {
    vi.mocked(api.setProjectAiModel).mockResolvedValueOnce({ profile_id: 'local', effective_profile: local, thinking: false })
      .mockResolvedValueOnce({ profile_id: null, effective_profile: cloud, thinking: false })
    const { onChanging } = setup()
    expect(await openMenu()).toHaveAttribute('aria-checked', 'true')
    fireEvent.click(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ }))
    await waitFor(() => expect(screen.queryByRole('menu')).not.toBeInTheDocument())
    expect(api.setProjectAiModel).toHaveBeenCalledWith('project', 'local')
    expect(onChanging).toHaveBeenCalledWith(true)
    expect(onChanging).toHaveBeenLastCalledWith(false)
    const defaultOption = await openMenu()
    expect(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ })).toHaveAttribute('aria-checked', 'true')
    fireEvent.click(defaultOption)
    await waitFor(() => expect(screen.queryByRole('menu')).not.toBeInTheDocument())
    expect(api.setProjectAiModel).toHaveBeenLastCalledWith('project', null)
    expect(await openMenu()).toHaveAttribute('aria-checked', 'true')
  })

  it('attiva il ragionamento approfondito con lo switch accanto al modello', async () => {
    vi.mocked(api.projectAiModel).mockResolvedValue({
      profile_id: 'cloud', effective_profile: cloud, thinking: false })
    vi.mocked(api.setProjectAiModel).mockResolvedValue({
      profile_id: 'cloud', effective_profile: cloud, thinking: true })
    setup()
    const toggle = await screen.findByRole('switch', { name: 'Ragionamento approfondito' })
    expect(toggle).toHaveAttribute('aria-checked', 'false')
    fireEvent.click(toggle)
    await waitFor(() => expect(api.setProjectAiModel)
      .toHaveBeenCalledWith('project', 'cloud', true))
    expect(toggle).toHaveAttribute('aria-checked', 'true')
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('salva il thinking usando il predefinito senza selezionare un profilo specifico', async () => {
    vi.mocked(api.setProjectAiModel).mockResolvedValue({
      profile_id: null, effective_profile: cloud, thinking: true })
    setup()
    const toggle = await screen.findByRole('switch', { name: 'Ragionamento approfondito' })
    expect(toggle).toBeEnabled()
    fireEvent.click(toggle)
    await waitFor(() => expect(api.setProjectAiModel).toHaveBeenCalledWith('project', null, true))
    expect(toggle).toHaveAttribute('aria-checked', 'true')
    expect(await openMenu()).toHaveAttribute('aria-checked', 'true')
  })

  it('conserva lo stato del thinking quando il salvataggio fallisce', async () => {
    vi.mocked(api.setProjectAiModel).mockRejectedValue(new Error('Salvataggio non riuscito'))
    setup()
    const toggle = await screen.findByRole('switch', { name: 'Ragionamento approfondito' })
    fireEvent.click(toggle)
    await openMenu()
    expect(await screen.findByRole('alert')).toHaveTextContent('Salvataggio non riuscito')
    expect(toggle).toHaveAttribute('aria-checked', 'false')
    expect(toggle).toBeEnabled()
  })

  it('keeps the old selection when saving fails', async () => {
    vi.mocked(api.setProjectAiModel).mockRejectedValue(new Error('Salvataggio non riuscito'))
    setup()
    const defaultOption = await openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Salvataggio non riuscito')
    expect(defaultOption).toHaveAttribute('aria-checked', 'true')
    expect(defaultOption).toBeEnabled()
  })

  it('disables changes while an operation is running', async () => {
    setup(true)
    expect(await screen.findByRole('switch', { name: 'Ragionamento approfondito' })).toBeDisabled()
    expect(await openMenu()).toBeDisabled()
    expect(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ })).toBeDisabled()
  })

  it('ignores an old save response after moving to another project', async () => {
    let resolve!: (selection: ProjectAiSelection) => void
    vi.mocked(api.setProjectAiModel).mockReturnValue(new Promise((done) => { resolve = done }))
    const { rerender, onChanging } = setup()
    await openMenu()
    fireEvent.click(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ }))
    expect(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ })).toBeDisabled()
    rerender(<MemoryRouter><ProjectModelSelector projectId="another" onChanging={onChanging} /></MemoryRouter>)
    const defaultOption = await openMenu()
    expect(defaultOption).toBeEnabled()
    await act(async () => resolve({ profile_id: 'local', effective_profile: local, thinking: false }))
    expect(defaultOption).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('menu')).toBeVisible()
    expect(api.projectAiModel).toHaveBeenLastCalledWith('another', expect.any(AbortSignal))
  })

  it('links to settings when no model is configured', async () => {
    vi.mocked(api.aiSettings).mockResolvedValue({ providers, profiles: [], default_profile_id: null })
    vi.mocked(api.projectAiModel).mockResolvedValue({ profile_id: null, effective_profile: null, thinking: false })
    setup()
    expect(await openMenu()).toBeDisabled()
    expect(screen.getByRole('menuitem', { name: 'Gestisci modelli' })).toHaveAttribute('href', '/settings')
    expect(screen.getByText('Aggiungi un modello nelle impostazioni per iniziare.')).toBeVisible()
  })

  it('opens the composer menu, navigates with the keyboard and saves without submitting the chat', async () => {
    const submit = vi.fn((event) => event.preventDefault())
    vi.mocked(api.setProjectAiModel).mockResolvedValue({ profile_id: 'local', effective_profile: local, thinking: false })
    render(<MemoryRouter><form onSubmit={submit}>
      <ProjectModelSelector projectId="project" />
    </form></MemoryRouter>)
    const trigger = screen.getByRole('button', { name: 'Impostazioni AI' })
    expect(screen.queryByRole('combobox')).not.toBeInTheDocument()
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
    fireEvent.click(trigger)
    const defaultOption = await screen.findByRole('menuitemradio', { name: /Usa predefinito/ })
    await waitFor(() => expect(defaultOption).toHaveFocus())
    fireEvent.keyDown(defaultOption, { key: 'ArrowDown' })
    expect(screen.getByRole('menuitemradio', { name: /DeepSeek ufficio/ })).toHaveFocus()
    fireEvent.keyDown(document.activeElement!, { key: 'ArrowDown' })
    const localOption = screen.getByRole('menuitemradio', { name: /Ollama ufficio/ })
    expect(localOption).toHaveFocus()
    fireEvent.click(localOption)
    await waitFor(() => expect(screen.queryByRole('menu')).not.toBeInTheDocument())
    expect(api.setProjectAiModel).toHaveBeenCalledWith('project', 'local')
    expect(trigger).toHaveFocus()
    expect(submit).not.toHaveBeenCalled()
    fireEvent.click(trigger)
    expect(screen.getByRole('menuitemradio', { name: /Ollama ufficio/ })).toHaveAttribute('aria-checked', 'true')
    fireEvent.keyDown(screen.getByRole('menu'), { key: 'Escape' })
    expect(trigger).toHaveFocus()
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })

  it('keeps failed model changes visible in the menu and closes on an outside click', async () => {
    vi.mocked(api.setProjectAiModel).mockRejectedValue(new Error('Cambio non riuscito'))
    render(<MemoryRouter><ProjectModelSelector projectId="project" /></MemoryRouter>)
    fireEvent.click(screen.getByRole('button', { name: 'Impostazioni AI' }))
    fireEvent.click(await screen.findByRole('menuitemradio', { name: /Ollama ufficio/ }))
    expect(await screen.findByRole('alert')).toHaveTextContent('Cambio non riuscito')
    expect(screen.getByRole('menuitemradio', { name: /Usa predefinito/ })).toHaveAttribute('aria-checked', 'true')
    expect(screen.getByRole('menuitem', { name: 'Gestisci modelli' })).toHaveAttribute('href', '/settings')
    fireEvent.pointerDown(document.body)
    expect(screen.queryByRole('menu')).not.toBeInTheDocument()
  })
})
