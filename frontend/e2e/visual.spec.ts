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

test('markdown knowledge artifacts expose project and global scopes', async ({ page }, testInfo) => {
  await page.route(
    '**/api/projects/fondo-riqualificazione-2027/call-facts/extract',
    async (route) => {
      await route.fulfill({
        contentType: 'application/json',
        body: JSON.stringify({
          artifact: {
            id: 'fondo-riqualificazione-2027--call-facts',
            kind: 'call_facts',
            scope: 'project',
            title: 'Call Facts',
            filename: 'call-facts.md',
            status: 'Da verificare',
            byte_size: 342,
            version: 2,
            updated_at: '2026-08-03 18:00:00',
            editable: true,
            chunk_count: 1,
            content: '# Call Facts\n\n## Termine di candidatura\n\n15 settembre 2025',
          },
          fact_count: 2,
          missing_count: 1,
          evidence_count: 8,
          model: 'deepseek-test',
          total_tokens: 123,
        }),
      })
    },
  )
  await page.goto('/projects/fondo-riqualificazione-2027/settings')
  await page.getByRole('button', { name: 'Apri artefatti Markdown' }).click()

  await expect(page.getByRole('heading', { name: 'Conoscenza Markdown' })).toBeVisible()
  const callFactsEditor = page.getByLabel('Contenuto di Call Facts')
  await expect(callFactsEditor).toBeVisible()
  await expect(callFactsEditor).toContainText('# Call Facts')
  await expect(callFactsEditor).toBeEditable()

  await page.getByRole('button', { name: /Estrai dalle fonti|Riestrai dalle fonti/ }).click()
  await expect(callFactsEditor).toContainText('## Termine di candidatura')
  await expect(page.getByText('2 fatti estratti da 8 frammenti')).toBeVisible()

  await page.getByRole('button', { name: /Company Facts/ }).click()
  const companyEditor = page.getByLabel('Contenuto di Company Facts')
  await expect(companyEditor).toContainText('Mapi Ingegneria S.r.l.')
  await expect(companyEditor).not.toBeEditable()
  await expect(page.getByText('Gli artefatti globali sono in sola lettura')).toBeVisible()
  await expectNoHorizontalOverflow(page)
  await page.screenshot({
    path: `artifacts/${testInfo.project.name}-markdown-knowledge.png`,
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
