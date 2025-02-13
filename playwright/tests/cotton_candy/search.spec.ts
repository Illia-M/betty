import * as path from 'node:path'
import { Server, test as base } from '../index'
import { expect } from '@playwright/test'
import * as url from 'node:url'

const __dirname = url.fileURLToPath(new URL('.', import.meta.url))

const test = base.extend<{
  site: string,
}>({
  site: async ({ generateSite, temporaryDirectoryPath }, use) => {
    using server = new Server(path.join(temporaryDirectoryPath, 'output', 'www'))
    await generateSite(temporaryDirectoryPath, {
      url: await server.getPublicUrl(),
      extensions: {
        'cotton-candy': {},
        'gramps': {
          configuration: {
            family_trees: [
              {
                file: path.join(__dirname, '..', '..', 'fixtures', 'gramps.xml')
              }
            ]
          }
        }
      }
    })
    await use(await server.getPublicUrl())
  }
})

test('search, find, and navigate to a resource', async ({ page, site }) => {
  await page.goto(site)
  const searchQuery = page.locator('#search-query')
  await searchQuery.fill('Janet')
  await searchQuery.press('ArrowDown')
  await expect(page.locator('#search-results')).toBeVisible()
  await page.keyboard.press('ArrowDown')
  await page.locator(':focus').press('Enter')
  expect(page.url()).toBe(site + '/person/I0001/index.html')
  await page.close()
})
