import * as path from 'node:path'
import { buildApp, Server, test as base } from '../index'
import { expect } from '@playwright/test'

const test = base.extend<{
  site: string,
}>({
  site: async ({ temporaryDirectoryPath }, use) => {
    const projectDirectoryPath = await buildApp(temporaryDirectoryPath, {
      extensions: {
        'betty.extension.CottonCandy': {},
        'betty.extension.Gramps': {
          enabled: true,
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
    using server = new Server(path.join(projectDirectoryPath, 'output', 'www'))
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
  await expect(page.url()).toBe(site + '/person/I0001/index.html')
})
