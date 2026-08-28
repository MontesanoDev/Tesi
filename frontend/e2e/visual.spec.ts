import { expect, test } from '@playwright/test'

async function expectNoHorizontalOverflow(page: import('@playwright/test').Page) {
  const dimensions = await page.evaluate(() => ({
    clientWidth: document.documentElement.clientWidth,
    scrollWidth: document.documentElement.scrollWidth,
  }))
  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth)
}

test('project flow renders without overlap', async ({ page }, testInfo) => {
  await page.goto('/projects')
  await expect(page.getByRole('heading', { name: 'Progetti' })).toBeVisible()
  await expect(page.getByText('Fondo Riqualificazione 2027')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-projects.png`,
    fullPage: true,
  })

  await page.getByText('Fondo Riqualificazione 2027').first().click()
  await expect(page.getByPlaceholder('Come posso aiutarti in questo progetto?')).toBeVisible()
  await expect(page.getByText('Fondo_Riqualificazione_2027.pdf')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-workspace.png`,
    fullPage: true,
  })

  await page.route('**/api/projects/fondo-riqualificazione-2027/answer', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        conversation_id: 'conv-scadenza-test',
        turn_id: 101,
        question: 'Qual è la scadenza?',
        answer: 'La scadenza è fissata alle ore 12.00 del 15.09.2025 [1].',
        citations: [1],
        missing_information: [],
        evidence: [
          {
            chunk_id: 1,
            file_id: 1,
            source_name: 'Fondo_Riqualificazione_2027.pdf',
            chunk_index: 17,
            excerpt: 'Il termine di scadenza è fissato alle ore 12.00 del 15.09.2025.',
            relevance: 5.7,
          },
        ],
        generation_status: 'completed',
        model: 'deepseek-test',
        total_tokens: 42,
        notice: null,
      }),
    })
  })
  const composer = page.getByPlaceholder('Come posso aiutarti in questo progetto?')
  await composer.fill('Qual è')
  await composer.press('Shift+Enter')
  await composer.pressSequentially('la scadenza?')
  await expect(composer).toHaveValue('Qual è\nla scadenza?')
  await composer.press('Enter')
  await expect(page.getByText('Risposta Mapi')).toBeVisible()
  await expect(page.getByText('Evidenze recuperate', { exact: true })).toBeVisible()
  const citedSource = page.locator('.evidence-results').getByText('Fondo_Riqualificazione_2027.pdf')
  await expect(citedSource).not.toBeVisible()
  await page.getByText('Evidenze recuperate', { exact: true }).click()
  await expect(citedSource).toBeVisible()
  await expect(composer).toBeInViewport()
  await expectNoHorizontalOverflow(page)

  await page.getByRole('button', { name: 'Menu progetto' }).click()
  await page.getByRole('button', { name: /Impostazioni progetto/ }).click()
  await expect(page.getByRole('heading', { name: 'Impostazioni progetto' })).toBeVisible()
  await expect(page.getByText('Fonti globali rese disponibili nel progetto corrente')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-project-settings.png`,
    fullPage: true,
  })
})

test('project deletion requires confirmation and returns to the project list', async ({ page }, testInfo) => {
  let deleteRequests = 0
  await page.route(
    /\/api\/projects\/fondo-riqualificazione-2027$/,
    async (route) => {
      if (route.request().method() !== 'DELETE') {
        await route.continue()
        return
      }
      deleteRequests += 1
      await route.fulfill({ status: 204, body: '' })
    },
  )

  await page.goto('/projects/fondo-riqualificazione-2027')
  await page.getByRole('button', { name: 'Menu progetto' }).click()
  await page.getByRole('button', { name: 'Elimina progetto' }).click()
  await expect(page.getByRole('dialog', { name: 'Elimina progetto' })).toBeVisible()
  await expect(page.getByText("La conoscenza globale dell'azienda non verrà eliminata.")).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-delete-project.png`,
    fullPage: true,
  })

  await page.getByRole('button', { name: 'Elimina definitivamente' }).click()
  await expect(page).toHaveURL(/\/projects$/)
  await expect(page.getByRole('heading', { name: 'Progetti' })).toBeVisible()
  expect(deleteRequests).toBe(1)
})

test('document review keeps source provenance visible', async ({ page }, testInfo) => {
  await page.goto('/projects/fondo-riqualificazione-2027/review')
  await expect(page.getByRole('heading', { name: 'Modulo di candidatura A' }).first()).toBeVisible()
  await expect(page.getByText("L'approvazione finale spetta al revisore umano.")).toBeVisible()
  await expectNoHorizontalOverflow(page)
  const paperDimensions = await page.locator('.document-preview').evaluate((element) => ({
    clientWidth: element.clientWidth,
    scrollWidth: element.scrollWidth,
  }))
  expect(paperDimensions.scrollWidth).toBeLessThanOrEqual(paperDimensions.clientWidth)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-review.png`,
    fullPage: true,
  })
})

test('company knowledge is managed in the global archive', async ({ page }, testInfo) => {
  const documents = [
    {
      id: 41,
      name: 'curriculum-mapi.pdf',
      category: 'company',
      metadata: 'PDF · 840 KB · 18 frammenti',
      status: 'Indicizzato',
      mime_type: 'application/pdf',
      byte_size: 860160,
      page_count: 8,
      chunk_count: 18,
    },
    {
      id: 40,
      name: 'norme-tecniche.txt',
      category: 'general',
      metadata: 'TXT · 12 KB · 4 frammenti',
      status: 'Indicizzato',
      mime_type: 'text/plain',
      byte_size: 12288,
      page_count: 1,
      chunk_count: 4,
    },
  ]
  let uploadCount = 0
  let profileContent = '# Profilo operativo\n\nMapi supporta la progettazione per enti committenti.\n'

  await page.route(/\/api\/projects\/fondo-riqualificazione-2027$/, async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        id: 'fondo-riqualificazione-2027',
        title: 'Fondo Riqualificazione 2027',
        description: 'Preparazione della candidatura tecnica',
        status: 'In analisi',
        status_tone: 'info',
        updated_label: 'ora',
        source_count: 1,
        model_count: 1,
        instructions: '',
        call_fact_count: 14,
        missing_fact_count: 2,
        files: [],
        knowledge_sources: [],
        conversations: [],
      }),
    })
  })
  await page.route(/\/api\/global-knowledge$/, async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        documents,
        document_count: documents.length,
        chunk_count: documents.reduce((total, document) => total + document.chunk_count, 0),
      }),
    })
  })
  await page.route(/\/api\/global-knowledge\/files$/, async (route) => {
    uploadCount += 1
    const uploaded = uploadCount === 1
      ? {
          id: 42,
          name: 'certificazione-iso.txt',
          category: 'company',
          metadata: 'TXT · 1 KB · 2 frammenti',
          status: 'Indicizzato',
          mime_type: 'text/plain',
          byte_size: 512,
          page_count: 1,
          chunk_count: 2,
        }
      : {
          id: 43,
          name: 'profilo-operativo.md',
          category: 'company',
          metadata: 'MD · 1 KB · 1 frammento',
          status: 'Indicizzato',
          mime_type: 'text/markdown',
          byte_size: 180,
          page_count: 1,
          chunk_count: 1,
        }
    documents.unshift(uploaded)
    await route.fulfill({
      status: 201,
      contentType: 'application/json',
      body: JSON.stringify(uploaded),
    })
  })
  await page.route(/\/api\/global-knowledge\/files\/43\/content$/, async (route) => {
    if (route.request().method() === 'PUT') {
      profileContent = (route.request().postDataJSON() as { content: string }).content
    }
    const document = documents.find((item) => item.id === 43)
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({ ...document, content: profileContent }),
    })
  })
  await page.goto('/settings')
  await expect(page.getByRole('heading', { name: 'Impostazioni generali' })).toBeVisible()
  await expect(page.getByRole('tab', { name: 'Company KB' })).not.toBeVisible()

  await page.goto('/company-knowledge')
  await expect(page.getByRole('heading', { name: 'Dati aziendali e conoscenza' })).toBeVisible()
  await expect(page.getByText('curriculum-mapi.pdf')).toBeVisible()
  await expect(page.getByText('norme-tecniche.txt')).not.toBeVisible()
  await page.locator('input[type="file"]').setInputFiles({
    name: 'certificazione-iso.txt',
    mimeType: 'text/plain',
    buffer: Buffer.from('Certificazione ISO 9001 per servizi di ingegneria.'),
  })
  await expect(page.getByText('certificazione-iso.txt aggiunto a Company KB in 2 frammenti.')).toBeVisible()
  await expect(page.getByText('2 documenti', { exact: true })).toBeVisible()
  await page.getByRole('button', { name: 'Aggiungi contenuto testuale' }).click()
  await page.getByLabel('Titolo').fill('Profilo operativo')
  await page.getByLabel('Contenuto Markdown').fill('Mapi supporta la progettazione per enti committenti.')
  await page.getByRole('button', { name: 'Salva in Company KB' }).click()
  await expect(page.getByText('profilo-operativo.md aggiunto a Company KB in 1 frammento.')).toBeVisible()
  await expect(page.getByText('profilo-operativo.md', { exact: true })).toBeVisible()
  await expect(page.getByText('3 documenti', { exact: true })).toBeVisible()
  await expect(page.getByRole('button', { name: 'Modifica curriculum-mapi.pdf' })).toHaveCount(0)
  await page.getByRole('button', { name: 'Modifica profilo-operativo.md' }).click()
  await expect(page.getByRole('heading', { name: 'Modifica profilo-operativo.md' })).toBeVisible()
  await page.getByLabel('Contenuto Markdown').fill(
    '# Profilo operativo\n\nMapi supporta progettazione e direzione lavori.',
  )
  await page.getByRole('button', { name: 'Salva modifiche' }).click()
  await expect(page.getByText('profilo-operativo.md aggiornato e reindicizzato in 1 frammento.')).toBeVisible()
  await page.getByRole('tab', { name: 'General KB' }).click()
  await expect(page.getByText('norme-tecniche.txt')).toBeVisible()
  await expect(page.getByText('curriculum-mapi.pdf')).not.toBeVisible()
  await expect(page.getByRole('tab', { name: 'Company Facts' })).not.toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-company-kb-global.png`,
    fullPage: true,
  })

  await page.goto('/projects/fondo-riqualificazione-2027/settings')
  await expect(page.getByRole('heading', { name: 'Impostazioni progetto' })).toBeVisible()
  await expect(page.getByText('Conoscenza condivisa')).toHaveCount(0)
  await expect(page.getByText('curriculum-mapi.pdf')).toHaveCount(0)
  await expect(page.getByText('norme-tecniche.txt')).toHaveCount(0)
  await expect(page.getByRole('heading', { name: 'Call Facts' })).toBeVisible()
  await expect(page.getByText('Scope controllato')).toHaveCount(0)
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-company-kb-project.png`,
    fullPage: true,
  })
})

test('markdown knowledge artifacts expose project and global scopes', async ({ page }, testInfo) => {
  let factStatus: 'pending' | 'verified' = 'pending'
  let factTitle = 'Termine di candidatura'
  let factValue = '15 settembre 2025'
  let artifactVersion = 4
  const callFactsArtifact = () => ({
    id: 'fondo-riqualificazione-2027--call-facts',
    kind: 'call_facts',
    scope: 'project',
    title: 'Call Facts',
    filename: 'call-facts.md',
    status: factStatus === 'verified' ? 'Verificato' : 'Da verificare',
    byte_size: 342,
    version: artifactVersion,
    updated_at: '2026-08-04 18:00:00',
    editable: true,
    chunk_count: factStatus === 'verified' ? 1 : 0,
    content: [
      '# Call Facts',
      '',
      `## ${factTitle}`,
      '',
      '<!-- fact-id: cf-demo -->',
      '',
      `**Valore:** ${factValue}`,
      '',
      `**Stato:** ${factStatus === 'verified' ? 'Verificato' : 'Da verificare'}`,
      '',
      '**Fonti:**',
      '- avviso.pdf, frammento 18',
    ].join('\n'),
  })
  const reviewPayload = () => ({
    artifact: callFactsArtifact(),
    facts: [
      {
        id: 'cf-demo',
        title: factTitle,
        value: factValue,
        status: factStatus,
        sources: [{ name: 'avviso.pdf', fragment: 18 }],
      },
    ],
    missing_information: [],
    pending_count: factStatus === 'pending' ? 1 : 0,
    verified_count: factStatus === 'verified' ? 1 : 0,
    discarded_count: 0,
  })
  let draftGenerated = false
  const draftArtifact = () => ({
    id: 'fondo-riqualificazione-2027--draft',
    kind: 'output_draft',
    scope: 'project',
    title: 'Draft',
    filename: 'draft.md',
    status: draftGenerated ? 'Da verificare' : 'Da generare',
    byte_size: 640,
    version: draftGenerated ? 2 : 1,
    updated_at: '2026-08-04 18:10:00',
    editable: true,
    chunk_count: 0,
    content: draftGenerated
      ? [
          '# Candidatura',
          '',
          'Termine: 15 settembre 2025 [CF:cf-demo]',
          '',
          'Importo: [TODO: inserire importo richiesto]',
          '',
          '# Provenienza',
          '',
          '- [CF:cf-demo] Termine di candidatura - avviso.pdf, frammento 18',
        ].join('\n')
      : '# Draft candidatura\n\n> Generare il documento dal template.',
  })

  await page.route(
    '**/api/projects/fondo-riqualificazione-2027/call-facts',
    async (route) => {
      await route.fulfill({ contentType: 'application/json', body: JSON.stringify(reviewPayload()) })
    },
  )
  await page.route(
    /\/api\/projects\/fondo-riqualificazione-2027\/call-facts\/cf-demo$/,
    async (route) => {
      const payload = route.request().postDataJSON() as {
        action: 'verify' | 'edit'
        title?: string
        value?: string
      }
      artifactVersion += 1
      if (payload.action === 'verify') factStatus = 'verified'
      if (payload.action === 'edit') {
        factStatus = 'pending'
        factTitle = payload.title ?? factTitle
        factValue = payload.value ?? factValue
      }
      await route.fulfill({ contentType: 'application/json', body: JSON.stringify(reviewPayload()) })
    },
  )
  await page.route(
    '**/api/projects/fondo-riqualificazione-2027/call-facts/extract',
    async (route) => {
      artifactVersion += 1
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          artifact: callFactsArtifact(),
          fact_count: 2,
          missing_count: 1,
          evidence_count: 8,
          model: 'deepseek-test',
          total_tokens: 123,
        }),
      })
    },
  )
  await page.route(
    '**/api/projects/fondo-riqualificazione-2027/artifacts/fondo-riqualificazione-2027--draft',
    async (route) => {
      await route.fulfill({ contentType: 'application/json', body: JSON.stringify(draftArtifact()) })
    },
  )
  await page.route(
    '**/api/projects/fondo-riqualificazione-2027/draft/generate',
    async (route) => {
      draftGenerated = true
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          artifact: draftArtifact(),
          verified_fact_count: 1,
          used_fact_count: 1,
          missing_information: ['Importo richiesto'],
          model: 'deepseek-test',
          total_tokens: 120,
        }),
      })
    },
  )
  await page.goto('/projects/fondo-riqualificazione-2027/settings')
  await page.getByRole('button', { name: 'Apri artefatti Markdown' }).click()

  await expect(page.getByRole('heading', { name: 'Conoscenza Markdown' })).toBeVisible()
  await expect(page.getByRole('heading', { name: 'Termine di candidatura' })).toBeVisible()
  await expect(page.getByText('avviso.pdf, frammento 18')).toBeVisible()

  await page.getByRole('button', { name: 'Verifica', exact: true }).click()
  await expect(page.getByText('verificato e reso disponibile al RAG')).toBeVisible()
  await page.getByRole('tab', { name: 'Verificati 1' }).click()
  await expect(page.getByRole('heading', { name: 'Termine di candidatura' })).toBeVisible()

  await page.getByRole('button', { name: 'Modifica', exact: true }).click()
  await page.getByLabel('Titolo').fill('Termine e orario della candidatura')
  await page.getByLabel('Valore').fill('Ore 12 del 15 settembre 2025')
  await page.getByRole('button', { name: 'Salva modifica' }).click()
  await page.getByRole('tab', { name: 'Da verificare 1' }).click()
  await expect(page.getByRole('heading', { name: 'Termine e orario della candidatura' })).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-call-facts-review.png`,
    fullPage: true,
  })

  await page.getByRole('tab', { name: 'Markdown' }).click()
  const callFactsEditor = page.getByLabel('Contenuto di Call Facts')
  await expect(callFactsEditor).toBeVisible()
  await expect(callFactsEditor).toContainText('Termine e orario della candidatura')
  await expect(callFactsEditor).toBeEditable()

  await page.getByRole('button', { name: /Estrai dalle fonti|Riestrai dalle fonti/ }).click()
  await expect(callFactsEditor).toContainText('## Termine e orario della candidatura')
  await expect(page.getByText('2 fatti estratti da 8 frammenti')).toBeVisible()

  await page.getByRole('button', { name: /General KB/ }).click()
  const generalEditor = page.getByLabel('Contenuto di General KB')
  await expect(generalEditor).not.toBeEditable()
  await expect(page.getByText('Gli artefatti globali sono in sola lettura')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-markdown-knowledge.png`,
    fullPage: true,
  })

  await page.locator('.artifact-list-item').filter({ hasText: 'Call Facts' }).click()
  await page.getByRole('button', { name: 'Verifica', exact: true }).click()
  await page.locator('.artifact-list-item').filter({ hasText: 'Template' }).click()
  await page.getByRole('button', { name: 'Genera draft', exact: true }).click()
  await expect(page.getByRole('heading', { name: 'Draft', exact: true })).toBeVisible()
  await expect(page.getByText('Output escluso dal RAG')).toBeVisible()
  await expect(page.getByLabel('Contenuto di Draft')).toContainText(
    'Termine: 15 settembre 2025 [CF:cf-demo]',
  )
  await expect(page.getByText('Draft generato da 1 di 1 Call Facts verificati · 1 TODO.')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-generated-draft.png`,
    fullPage: true,
  })
})

test('missing evidence is explained as an assistant answer', async ({ page }) => {
  await page.route('**/api/projects/fondo-riqualificazione-2027/answer', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        conversation_id: 'conv-no-evidence-test',
        turn_id: 201,
        question: 'Come posso contattarlo?',
        answer: 'Non trovo nelle fonti indicizzate informazioni sufficienti per rispondere in modo verificabile.',
        citations: [],
        missing_information: ['Una fonte contenente il recapito richiesto'],
        evidence: [],
        generation_status: 'no_evidence',
        model: null,
        total_tokens: null,
        notice: 'Le fonti non contengono dati verificabili per questa richiesta.',
      }),
    })
  })

  await page.goto('/projects/fondo-riqualificazione-2027')
  const composer = page.getByPlaceholder('Come posso aiutarti in questo progetto?')
  await composer.fill('Come posso contattarlo?')
  await composer.press('Enter')

  await expect(page.getByText('Le fonti non contengono dati verificabili')).toBeVisible()
  await expect(page.getByText('Non trovo nelle fonti indicizzate')).toBeVisible()
  await expect(page.getByText('Una fonte contenente il recapito richiesto')).toBeVisible()
})

test('conversation preserves earlier turns without project evidence', async ({ page }, testInfo) => {
  const conversationId = 'conv-history-test'
  const persistedTurns: Array<Record<string, unknown>> = []

  await page.route(
    `**/api/projects/fondo-riqualificazione-2027/conversations/${conversationId}`,
    async (route) => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          id: conversationId,
          project_id: 'fondo-riqualificazione-2027',
          title: 'Chi sei?',
          metadata: `Ora · ${persistedTurns.length} messaggi`,
          target: 'chat',
          turns: persistedTurns,
        }),
      })
    },
  )
  await page.route('**/api/projects/fondo-riqualificazione-2027/answer', async (route) => {
    const { question, conversation_id } = route.request().postDataJSON() as {
      question: string
      conversation_id: string | null
    }
    const firstQuestion = question === 'Chi sei?'
    expect(conversation_id).toBe(firstQuestion ? null : conversationId)
    const turnId = persistedTurns.length + 1
    const turn = {
      id: turnId,
      question,
      answer: firstQuestion
        ? 'Sono Mapi RAG, un assistente tecnico per progetti di ingegneria civile.'
        : 'Il mio nome è Mapi RAG.',
      citations: [],
      missing_information: [],
      evidence: [],
      generation_status: 'direct',
      model: 'Mapi RAG',
      total_tokens: 0,
      notice: null,
    }
    persistedTurns.push(turn)
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        ...turn,
        conversation_id: conversationId,
        turn_id: turnId,
      }),
    })
  })

  await page.goto('/projects/fondo-riqualificazione-2027')
  const composer = page.getByPlaceholder('Come posso aiutarti in questo progetto?')
  await composer.fill('Chi sei?')
  await composer.press('Enter')

  await expect(page.getByText('Risposta diretta di Mapi RAG.')).toBeVisible()
  await expect(page.getByText('Sono Mapi RAG, un assistente tecnico')).toBeVisible()

  await composer.fill('Come ti chiami?')
  await composer.press('Enter')

  await expect(page.locator('.chat-turn')).toHaveCount(2)
  await expect(page.getByText('Chi sei?', { exact: true })).toBeVisible()
  await expect(page.getByText('Sono Mapi RAG, un assistente tecnico')).toBeVisible()
  await expect(page.getByText('Come ti chiami?', { exact: true })).toBeVisible()
  await expect(page.getByText('Il mio nome è Mapi RAG.')).toBeVisible()
  await expect(page.getByText('Evidenze recuperate', { exact: true })).toHaveCount(0)
  await expect(page).toHaveURL(
    `/projects/fondo-riqualificazione-2027/conversations/${conversationId}`,
  )

  await page.reload()
  await expect(page.locator('.chat-turn')).toHaveCount(2)
  await expect(page.getByText('Chi sei?', { exact: true })).toBeVisible()
  await expect(page.getByText('Il mio nome è Mapi RAG.')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-conversation-history.png`,
    fullPage: true,
  })
})
