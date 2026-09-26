import { expect, test } from '@playwright/test'
import { resolve } from 'node:path'
import { pathToFileURL } from 'node:url'

const root = resolve(import.meta.dirname, '../..')
const presentation = pathToFileURL(resolve(root, 'presentazione-retrieval.html')).href

test('offline presentation, strategies, examples and dialogs', async ({ page }, testInfo) => {
  const errors: string[] = []
  const requests: string[] = []
  page.on('pageerror', (error) => errors.push(error.message))
  page.on('request', (request) => { if (/^https?:/.test(request.url())) requests.push(request.url()) })
  await page.goto(presentation)
  await expect(page.getByRole('heading', { name: 'Il retrieval di Mapi RAG', exact: true })).toBeVisible()
  expect(await page.locator('.product-figure img').evaluate((image: HTMLImageElement) => image.complete && image.naturalWidth > 0)).toBe(true)
  await expect(page.getByRole('button', { name: 'Schermata precedente' })).toBeDisabled()
  for (let slide = 0; slide < 4; slide++) {
    await page.locator(`[data-slide="${slide}"]`).click()
    await expect(page.locator(`#slide-${slide + 1}`)).toBeVisible()
    await expect(page.locator('.slide:visible')).toHaveCount(1)
    const dimensions = await page.evaluate(() => {
      const deck = document.querySelector('#deck')!
      return { width: document.documentElement.clientWidth, content: document.documentElement.scrollWidth, inner: deck.clientHeight, scroll: deck.scrollHeight }
    })
    expect(dimensions.content).toBeLessThanOrEqual(dimensions.width)
    if (testInfo.project.name === 'desktop') expect(dimensions.scroll).toBeLessThanOrEqual(dimensions.inner + 1)
    await page.screenshot({ path: `artifacts/retrieval/${testInfo.project.name}-${slide + 1}.png`, animations: 'disabled' })
  }
  await expect(page.getByRole('button', { name: 'Schermata successiva' })).toBeDisabled()
  await page.getByRole('button', { name: 'Entrambe le evidenze' }).click()
  await expect(page.locator('#recall-value')).toHaveText('100%')
  await expect(page.locator('#precision-value')).toHaveText('50%')
  await page.getByRole('button', { name: 'Una evidenza', exact: true }).click()
  await expect(page.locator('#recall-value')).toHaveText('50%')
  await expect(page.locator('#precision-value')).toHaveText('25%')

  await page.locator('[data-slide="1"]').click()
  await page.getByRole('tab', { name: /Vettoriale/ }).click()
  await expect(page.locator('#strategy-panel')).toHaveAttribute('data-mode', 'dense')
  await page.getByRole('tab', { name: /Vettoriale/ }).press('ArrowRight')
  await expect(page.getByRole('tab', { name: /Ibrido/ })).toHaveAttribute('aria-selected', 'true')
  await expect(page.locator('#fusion-label')).toHaveText('Fusione RRF')
  await expect(page.locator('#page-label')).toHaveText('02 / 04')
  await page.screenshot({ path: `artifacts/retrieval/${testInfo.project.name}-hybrid.png`, animations: 'disabled' })

  await page.getByRole('button', { name: 'Fonti della ricerca' }).click()
  const sources = page.getByRole('dialog', { name: 'Fonti della ricerca' })
  await expect(sources).toBeVisible()
  await expect(sources.getByRole('link')).toHaveCount(9)
  await page.keyboard.press('ArrowRight')
  await expect(page.locator('#page-label')).toHaveText('02 / 04')
  await page.keyboard.press('Escape')
  await expect(sources).toBeHidden()
  await expect(page.getByRole('button', { name: 'Fonti della ricerca' })).toBeFocused()

  await page.getByRole('button', { name: 'Note per la discussione' }).click()
  await expect(page.locator('#notes-content')).toContainText('RRF combina posizioni')
  await page.mouse.click(2, 2)
  await expect(page.locator('#notes-dialog')).toBeHidden()
  await page.keyboard.press('Home')
  await page.getByRole('button', { name: 'Ingrandisci il prototipo' }).click()
  await expect(page.locator('#image-dialog')).toBeVisible()
  await page.getByRole('button', { name: 'Chiudi immagine' }).click()
  if (testInfo.project.name === 'desktop') {
    await page.getByRole('button', { name: 'Schermo intero', exact: true }).click()
    await expect(page.getByRole('button', { name: 'Esci da schermo intero' })).toBeVisible()
    await page.getByRole('button', { name: 'Esci da schermo intero' }).click()
    await expect(page.getByRole('button', { name: 'Schermo intero', exact: true })).toBeVisible()
  }

  await page.evaluate(() => { window.print = () => { document.documentElement.dataset.printRequested = 'true' } })
  await page.getByRole('button', { name: 'Stampa o salva in PDF' }).click()
  await expect(page.locator('html')).toHaveAttribute('data-print-requested', 'true')
  await page.emulateMedia({ media: 'print' })
  await expect(page.locator('.slide:visible')).toHaveCount(4)
  await expect(page.locator('.masthead')).toBeHidden()
  if (testInfo.project.name === 'desktop') await page.pdf({ path: resolve(root, 'presentazione-retrieval.pdf'), preferCSSPageSize: true, printBackground: true })
  await page.emulateMedia({ media: 'screen' })
  await expect(page.locator('.slide:visible')).toHaveCount(1)
  expect(requests).toEqual([])
  expect(errors).toEqual([])
})

test('laptop, wide display, deep links and reduced motion', async ({ page }, testInfo) => {
  test.skip(testInfo.project.name !== 'desktop')
  await page.emulateMedia({ reducedMotion: 'reduce' })
  await page.goto(`${presentation}#3`)
  await expect(page.locator('#page-label')).toHaveText('03 / 04')
  await page.keyboard.press('ArrowLeft')
  await expect(page.locator('#page-label')).toHaveText('02 / 04')
  await page.goBack()
  await expect(page.locator('#page-label')).toHaveText('03 / 04')
  for (const viewport of [{ width: 1366, height: 768 }, { width: 1920, height: 1080 }]) {
    await page.setViewportSize(viewport)
    for (let slide = 0; slide < 4; slide++) {
      await page.locator(`[data-slide="${slide}"]`).click()
      await expect(page.locator(`#slide-${slide + 1}`)).toBeVisible()
      const sizes = await page.locator('#deck').evaluate((element) => ({ client: element.clientHeight, scroll: element.scrollHeight, width: element.clientWidth, scrollWidth: element.scrollWidth }))
      expect(sizes.scrollWidth).toBeLessThanOrEqual(sizes.width)
      expect(sizes.scroll).toBeLessThanOrEqual(sizes.client + 1)
      await page.screenshot({ path: `artifacts/retrieval/${viewport.width}-${slide + 1}.png`, animations: 'disabled' })
    }
  }
  await page.keyboard.press('Home')
  expect(await page.locator('.pipeline li').first().evaluate((element) => getComputedStyle(element).animationName)).toBe('none')
  await page.goto(`${presentation}#invalid`)
  await expect(page.locator('#page-label')).toHaveText('01 / 04')
})
