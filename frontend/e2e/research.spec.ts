import { test, expect, type Page } from '@playwright/test'
import fs from 'node:fs/promises'

async function flagship(page: Page) {
  await page.getByRole('button', { name: 'Published rank reversal · rows 1 / 2 / 3' }).click()
  await expect(page.getByTestId('decision-ordering')).toBeVisible()
}

test.beforeEach(async ({ page }) => {
  await page.goto('/')
  await expect(page.getByRole('button', { name: 'Run screening', exact: true })).toBeEnabled()
})

test('default screening uses real API calculations', async ({ page }) => {
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  await expect(page.getByText('Calculated. Cited. Conditional.')).toBeVisible()
  await expect(page.locator('tbody tr')).toHaveCount(3)
  await expect(page.locator('tbody tr').last()).toContainText('1.324e-2')
})

test('generated goal follows temperature controls', async ({ page }) => {
  await page.getByLabel('Temperature', { exact: true }).fill('700')
  await expect(page.getByLabel('Research goal', { exact: true })).toHaveValue(/700 °C/)
  const response = page.waitForResponse((r) => r.url().endsWith('/api/screen'))
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  expect((await (await response).json()).resolved_plan.temperature_k).toBe(973.15)
  await expect(page.getByText('Calculated. Cited. Conditional.')).toBeVisible()
})

test('generated goal follows conductivity type', async ({ page }) => {
  await page.getByLabel('Conductivity type', { exact: true }).selectOption('total')
  await expect(page.getByLabel('Research goal', { exact: true })).toHaveValue(/total/)
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  await expect(page.getByText('The evidence is insufficient.')).toBeVisible()
  await expect(page.locator('.excluded-list')).toContainText('TYPE_NOT_COMPARABLE')
  await expect(page.locator('tbody')).toHaveCount(0)
})

test('manual contradictions are reported', async ({ page }) => {
  await page.getByLabel('Research goal', { exact: true }).fill('Find bulk conductors at 600 C')
  await page.getByLabel('Conductivity type', { exact: true }).selectOption('total')
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  await page.getByText('Resolved plan & global warnings').click()
  await expect(page.locator('.plan-details')).toContainText('CONFLICTING CONDUCTIVITY TYPE')
  await expect(page.getByLabel('Research goal', { exact: true })).toHaveValue(
    'Find bulk conductors at 600 C',
  )
})

test('humidity constraint abstains visibly', async ({ page }) => {
  await page
    .getByLabel('Research goal', { exact: true })
    .fill('Find bulk conductors at 600 °C that survive 10% humidity')
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  await expect(page.getByText('The evidence is insufficient.')).toBeVisible()
  await page.getByText('Resolved plan & global warnings').click()
  await expect(page.locator('.plan-details')).toContainText('UNVERIFIED CONSTRAINTS')
  await expect(page.locator('.plan-details')).toContainText('humidity')
  await page.screenshot({ path: '../artifacts/browser/humidity-abstention.png', fullPage: true })
})

test('flagship reversal, plot and slider use backend values', async ({ page }) => {
  await flagship(page)
  const first = page.locator('.ordering-row').first()
  await expect(first).toContainText('La0.95Sr0.05Ga0.95Mg0.05O2.95')
  await page.getByRole('button', { name: '1000 K', exact: true }).click()
  await expect(first).toContainText('La0.95Sr0.05Ga0.85Mg0.15O2.9')
  await expect(first).toContainText('6.712e-2')
  await expect(
    page.getByRole('img', {
      name: 'Temperature-dependent conductivity curves with regime boundaries',
    }),
  ).toBeVisible()
  await page.getByLabel('Decision temperature slider').focus()
  await page.getByLabel('Decision temperature slider').press('End')
  await expect(page.getByTestId('decision-ordering')).toContainText('1100.0000 K')
  await page.getByRole('button', { name: '1000 K', exact: true }).click()
  await page.locator('.curve-legend').scrollIntoViewIfNeeded()
  await page.screenshot({ path: '../artifacts/browser/temperature-explorer.png', fullPage: false })
  await page.getByText('Temperature analysis execution trace', { exact: true }).click()
  const trace = page.locator('.temperature-explorer').getByTestId('agent-execution-trace')
  await expect(trace).toContainText('analyze_temperature_interval')
  await expect(trace).toContainText('no model call')
})

test('exact regime boundary withholds its row', async ({ page }) => {
  await flagship(page)
  await page.locator('.regime-event').first().getByRole('button').click()
  await expect(page.getByTestId('decision-ordering')).toContainText('AT_TRANSITION')
  await expect(page.getByTestId('decision-ordering')).toContainText('Row 1 withheld')
})

test('continuous root displays a numerical tie rather than a strict winner', async ({ page }) => {
  await flagship(page)
  await page.locator('.continuous-event').first().getByRole('button').click()
  await expect(page.locator('.ordering-row .rank')).toHaveText(['1', '1', '3'])
  await expect(page.getByTestId('decision-ordering')).toContainText('tied with')
})

test('wrong-formula audit retains dimensional rejection', async ({ page }) => {
  await page.getByRole('button', { name: 'Wrong-formula audit' }).click()
  await expect(page.getByText('REJECTED WRONG FORMULA', { exact: false })).toBeVisible()
  await expect(page.locator('.adversarial-result')).toContainText('K·S/cm')
})

test('out-of-range refusal', async ({ page }) => {
  await page.getByRole('button', { name: 'Outside measured range' }).click()
  await expect(page.getByText('The evidence is insufficient.')).toBeVisible()
  await expect(page.locator('.excluded-list')).toContainText('OUTSIDE_MEASURED_RANGE')
})

test('source DOI navigation is inspectable', async ({ page }) => {
  await flagship(page)
  await page.getByText('Original formulas, fit parameters, validity ranges & provenance').click()
  const links = page.locator('.material-evidence a')
  await expect(links).toHaveCount(3)
  await expect(links.first()).toHaveAttribute(
    'href',
    'https://doi.org/10.1111/j.1151-2916.1998.tb02662.x',
  )
  // Link destination is verified; external publisher page availability is not claimed.
})

test('export contains real interval provenance and results', async ({ page }) => {
  await flagship(page)
  await expect(page.getByTestId('crossover-qualification')).toContainText(
    'Model-derived crossover temperatures; uncertainty bounds unavailable; experimental confirmation required.',
  )
  await expect(page.locator('.continuous-event h4').first()).toContainText('≈ 776 K')
  const pending = page.waitForEvent('download')
  await page.getByRole('button', { name: 'Export decision JSON' }).click()
  const download = await pending
  const report = JSON.parse(await fs.readFile((await download.path())!, 'utf8'))
  expect(report.source.dataset_doi).toBe('10.5281/zenodo.18947543')
  expect(report.selected_rankings.map((p: { ordering: number[] }) => p.ordering)).toEqual([
    [1, 2, 3],
    [3, 2, 1],
  ])
  expect(report.code_version.calculation_source_sha256).toHaveLength(64)
  expect(report.crossover_qualification).toContain('uncertainty bounds unavailable')
  expect(
    report.events.find((e: { exact_continuous_crossing: boolean }) => e.exact_continuous_crossing)
      .temperature_k,
  ).toBeCloseTo(776.407425051, 8)
})

test('responsive mobile viewport has no horizontal overflow', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 })
  await flagship(page)
  await expect(page.getByTestId('decision-ordering')).toBeVisible()
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(
    true,
  )
  await page.locator('.temperature-scrubber').scrollIntoViewIfNeeded()
  await page.screenshot({ path: '../artifacts/browser/mobile-explorer.png', fullPage: false })
})

test('API failure injection is displayed without candidates', async ({ page }) => {
  // Explicit synthetic failure injection; all other tests use the real Python API.
  await page.route('**/api/screen', (route) =>
    route.fulfill({
      status: 503,
      contentType: 'application/json',
      body: JSON.stringify({ detail: 'E2E_FAILURE_INJECTION' }),
    }),
  )
  await page.getByRole('button', { name: 'Run screening', exact: true }).click()
  await expect(page.getByRole('alert')).toContainText('E2E_FAILURE_INJECTION')
  await expect(page.locator('tbody')).toHaveCount(0)
})

test('offline agent screening shows an actual audited execution and export', async ({ page }) => {
  const panel = page.getByRole('region', { name: 'Research Agent execution' })
  await panel.getByRole('button', { name: 'Run research agent' }).click()
  const trace = panel.getByTestId('agent-execution-trace')
  await expect(trace).toContainText('COMPUTED')
  await expect(trace).toContainText('screen_published_records')
  await expect(trace).toContainText('no model call')
  const pending = page.waitForEvent('download')
  await panel.getByRole('button', { name: 'Export agent execution JSON' }).click()
  const exported = JSON.parse(await fs.readFile((await (await pending).path())!, 'utf8'))
  expect(exported.runtime_mode).toBe('OFFLINE_DETERMINISTIC')
  expect(exported.result.resolved_plan.temperature_k).toBe(873.15)
  expect(exported.result.candidates.map((c: { row_id: number }) => c.row_id)).toEqual([3, 2, 1])
  expect(exported.execution_trace.response_id).toBeNull()
  expect(exported.execution_trace.validated_arguments).toEqual(exported.validated_arguments)
  await panel.screenshot({ path: '../artifacts/browser/agent-screening.png' })
})

test('offline agent selects Huang interval by its explicit named source selection', async ({
  page,
}) => {
  const panel = page.getByRole('region', { name: 'Research Agent execution' })
  await panel.getByRole('button', { name: 'Huang interval question' }).click()
  await panel.getByLabel('Agent source row IDs').fill('')
  const response = page.waitForResponse((r) => r.url().endsWith('/api/research'))
  await panel.getByRole('button', { name: 'Run research agent' }).click()
  const result = (await (await response).json()).result
  expect(result.selected_rankings.map((p: { ordering: number[] }) => p.ordering)).toEqual([
    [1, 2, 3],
    [3, 2, 1],
  ])
  const trace = panel.getByTestId('agent-execution-trace')
  await expect(trace).toContainText('analyze_temperature_interval')
  await expect(trace).toContainText('772 meV')
  await expect(trace).toContainText('uncertainty bounds unavailable')
  await panel.screenshot({ path: '../artifacts/browser/agent-temperature.png' })
})

test('offline agent preserves humidity and lifetime in its refusal', async ({ page }) => {
  const panel = page.getByRole('region', { name: 'Research Agent execution' })
  await panel.getByRole('button', { name: 'Humidity and lifetime question' }).click()
  await panel.getByRole('button', { name: 'Run research agent' }).click()
  const trace = panel.getByTestId('agent-execution-trace')
  await expect(trace).toContainText('ABSTAINED')
  await expect(trace).toContainText('UNVERIFIED_CONSTRAINTS')
  await expect(trace).toContainText('10,000 operating hours')
  await expect(trace).toContainText('humidity')
  await panel.screenshot({ path: '../artifacts/browser/agent-refusal.png' })
})

test('unconfigured real agent fails without fallback and permits explicit offline run', async ({
  page,
}) => {
  expect((await (await page.request.get('/api/health')).json()).real_llm_status).toBe(
    'NOT_CONFIGURED',
  )
  const panel = page.getByRole('region', { name: 'Research Agent execution' })
  await panel.getByLabel('Agent runtime').selectOption('REAL_LLM')
  await panel.getByRole('button', { name: 'Run research agent' }).click()
  await expect(panel.getByRole('alert')).toContainText('UNAVAILABLE')
  await expect(panel.getByRole('alert')).toContainText('NOT_CONFIGURED')
  await expect(panel.getByTestId('agent-execution-trace')).toHaveCount(0)
  await panel.getByLabel('Agent runtime').selectOption('OFFLINE_DETERMINISTIC')
  await panel.getByRole('button', { name: 'Run research agent' }).click()
  await expect(panel.getByTestId('agent-execution-trace')).toContainText('no model call')
})

for (const scenario of ['A', 'B', 'C']) {
  test(`recorded genuine DeepSeek ${scenario} replay makes zero fresh planning requests`, async ({
    page,
  }) => {
    // Genuine archived provider evidence + real Python API. No fresh model inference.
    let planningPosts = 0
    page.on('request', (r) => {
      if (r.method() === 'POST' && r.url().endsWith('/api/research')) planningPosts++
    })
    const panel = page.getByRole('region', { name: 'Research Agent execution' })
    await panel
      .getByText('Recorded DeepSeek acceptance · zero new inference', { exact: true })
      .click()
    await panel.getByRole('button', { name: 'Load recorded DeepSeek traces' }).click()
    await panel.getByRole('button', { name: `Replay ${scenario}`, exact: true }).click()
    const notice = panel.getByTestId('recorded-trace-notice')
    await expect(notice).toContainText('RECORDED_TRACE_REPLAY')
    await expect(notice).toContainText('No fresh inference request')
    const trace = panel.getByTestId('agent-execution-trace')
    await expect(trace).toContainText('REAL_LLM — DeepSeek — deepseek-flash')
    await expect(trace).toContainText(scenario === 'C' ? 'ABSTAINED' : 'COMPUTED')
    if (scenario === 'B') await expect(trace).toContainText('SUPPORTED_MODEL_RANK_REVERSAL')
    if (scenario === 'C') {
      await expect(trace).toContainText('10,000 operating hours')
      await expect(trace).toContainText('BOTH_MODEL_PLAN_AND_INDEPENDENT_VALIDATOR')
      await expect(trace).toContainText('Executed scientific tool: none (validation only)')
    }
    const pending = page.waitForEvent('download')
    await panel.getByRole('button', { name: 'Export agent execution JSON' }).click()
    const exported = JSON.parse(await fs.readFile((await (await pending).path())!, 'utf8'))
    expect(exported.presentation_mode).toBe('RECORDED_TRACE_REPLAY')
    expect(exported.fresh_model_request).toBe(false)
    expect(exported.execution.execution_trace.response_id).toBeTruthy()
    expect(planningPosts).toBe(0)
    await panel.screenshot({
      path: `../artifacts/browser/deepseek-recorded-${scenario.toLowerCase()}.png`,
    })
  })
}
