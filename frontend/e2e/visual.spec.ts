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
  await expect(
    page.locator('.evidence-results').getByText('Fondo_Riqualificazione_2027.pdf'),
  ).toBeVisible()
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

test('assistant identity bypasses project evidence', async ({ page }) => {
  await page.route('**/api/projects/fondo-riqualificazione-2027/answer', async (route) => {
    await route.fulfill({
      contentType: 'application/json',
      body: JSON.stringify({
        question: 'Chi sei?',
        answer: 'Sono Mapi RAG, un assistente tecnico per progetti di ingegneria civile.',
        citations: [],
        missing_information: [],
        evidence: [],
        generation_status: 'direct',
        model: 'Mapi RAG',
        total_tokens: 0,
        notice: null,
      }),
    })
  })

  await page.goto('/projects/fondo-riqualificazione-2027')
  const composer = page.getByPlaceholder('Come posso aiutarti in questo progetto?')
  await composer.fill('Chi sei?')
  await composer.press('Enter')

  await expect(page.getByText('Risposta diretta di Mapi RAG.')).toBeVisible()
  await expect(page.getByText('Sono Mapi RAG, un assistente tecnico')).toBeVisible()
  await expect(page.getByText('Evidenze recuperate', { exact: true })).toHaveCount(0)
})
