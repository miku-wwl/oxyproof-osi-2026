import { test, expect } from '@playwright/test'
import fs from 'node:fs/promises'
import path from 'node:path'

// Real UI/API recording. Captions are presentation overlays, not app results.
test('record captioned scientific demonstration', async ({ page }) => {
  const start = Date.now()
  const scenes: { time_s: number; caption: string }[] = []
  async function caption(text: string, hold: number) {
    scenes.push({ time_s: (Date.now() - start) / 1000, caption: text })
    await page.evaluate((text) => {
      let el = document.getElementById('presentation-caption')
      if (!el) {
        el = document.createElement('div')
        el.id = 'presentation-caption'
        document.body.appendChild(el)
      }
      el.style.cssText =
        'position:fixed;bottom:16px;left:280px;right:30px;z-index:9999;padding:18px 24px;border-radius:8px;background:rgba(13,35,38,.96);color:#f6faf1;font:500 22px/1.5 Segoe UI,Arial,sans-serif;box-shadow:0 4px 20px #0003;pointer-events:none;'
      el.textContent = text
    }, text)
    await page.waitForTimeout(hold * 1000)
  }
  await page.goto('/')
  await expect(page.getByRole('button', { name: 'Run screening', exact: true })).toBeEnabled()
  await caption(
    'OxyProof — When the best material changes, can your AI explain why? A decision at one temperature does not establish the choice across an operating range.',
    15,
  )
  const pending = page.waitForResponse((r) => r.url().endsWith('/api/temperature-decisions'))
  await page.getByRole('button', { name: 'Published rank reversal · rows 1 / 2 / 3' }).click()
  const report = await (await pending).json()
  await page.locator('.curve-legend').evaluate((el) => el.scrollIntoView({ block: 'start' }))
  await caption(
    'Published evidence: three bulk records from the same report and method, measured over 600–1100 K. Curves use original fitted parameters and explicit units.',
    18,
  )
  await page
    .locator('.temperature-scrubber')
    .evaluate((el) => el.scrollIntoView({ block: 'start' }))
  await caption(
    'At 700 K, row 1 leads: 1 > 2 > 3. These are conditional model calculations from low-temperature fits, not new experimental observations.',
    20,
  )
  await page.getByRole('button', { name: '1000 K', exact: true }).click()
  await expect(page.locator('.ordering-row').first()).toContainText('La0.95Sr0.05Ga0.85Mg0.15O2.9')
  await caption(
    'At 1000 K, row 3 leads: 3 > 2 > 1. Higher activation energy can be offset by a larger prefactor; selected high-temperature regimes matter.',
    20,
  )
  await page.locator('.events-grid').evaluate((el) => el.scrollIntoView({ block: 'start' }))
  const roots = report.events
    .filter((e: { exact_continuous_crossing: boolean }) => e.exact_continuous_crossing)
    .map((e: { temperature_k: number }) => e.temperature_k.toFixed(0))
    .join(', ')
  await caption(
    `Model-derived crossings: approximately ${roots} K. Uncertainty bounds unavailable; experimental confirmation required. Published T* boundaries are separate events.`,
    22,
  )
  await page.locator('.regime-event').first().getByRole('button').click()
  await page
    .getByTestId('decision-ordering')
    .evaluate((el) => el.scrollIntoView({ block: 'start' }))
  await expect(page.getByTestId('decision-ordering')).toContainText('AT_TRANSITION')
  await caption(
    'At a published T*, the affected row is withheld. Fitted branches are not assumed continuous. The ±5 K neighborhood is a review heuristic, not uncertainty.',
    18,
  )
  await page.getByRole('button', { name: 'Wrong-formula audit' }).click()
  await expect(page.locator('.adversarial-result')).toBeVisible()
  await page.locator('.adversarial-result').evaluate((el) => el.scrollIntoView({ block: 'center' }))
  await caption(
    'Reusing this dataset’s A without 1/T yields K·S/cm, not conductivity. This educational counterexample does not accuse a specific source paper.',
    20,
  )
  await page
    .getByLabel('Research goal', { exact: true })
    .fill('Find bulk conductors at 600 C that survive 10% humidity')
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  await expect(page.getByText('The evidence is insufficient.')).toBeVisible()
  await page.getByText('Resolved plan & global warnings').click()
  await page.locator('.plan-details').evaluate((el) => el.scrollIntoView({ block: 'center' }))
  await caption(
    'A humidity requirement cannot disappear silently: UNVERIFIED_CONSTRAINTS. OxyProof abstains and proposes controlled humidity exposure and conductivity measurements.',
    22,
  )
  await page
    .locator('.temperature-explorer')
    .getByText('Original formulas, fit parameters, validity ranges & provenance')
    .click()
  const downloaded = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export decision JSON' }).click()
  const download = await downloaded
  const exported = JSON.parse(await fs.readFile((await download.path())!, 'utf8'))
  expect(exported.source.dataset_doi).toBe('10.5281/zenodo.18947543')
  await page
    .locator('.material-evidence')
    .first()
    .evaluate((el) => el.scrollIntoView({ block: 'start' }))
  await caption(
    'Export: dataset/source DOIs, raw row IDs, formulas, parameters, units, regimes, evidence verdicts and code fingerprint. Runtime: OFFLINE_DETERMINISTIC.',
    22,
  )
  await caption(
    'Our contribution is the auditable workflow on published evidence. No new material, experiment, validated uncertainty interval or humidity guarantee is claimed.',
    12,
  )
  const output = path.resolve(
    import.meta.dirname,
    '../../.local',
    process.env.OXYPROOF_DEMO_NAME ?? 'demo',
  )
  await fs.mkdir(output, { recursive: true })
  await fs.writeFile(path.join(output, 'exported-decision.json'), JSON.stringify(exported, null, 2))
  await fs.writeFile(
    path.join(output, 'scene-log.json'),
    JSON.stringify(
      {
        runtime_mode: report.runtime_mode,
        source_scope: report.source.scope,
        scenes,
        duration_at_last_scene_s: (Date.now() - start) / 1000,
      },
      null,
      2,
    ),
  )
  await page.close()
  await page.video()!.saveAs(path.join(output, 'oxyproof-phase2.webm'))
})
