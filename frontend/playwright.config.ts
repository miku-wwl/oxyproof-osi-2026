import { defineConfig } from '@playwright/test'
import path from 'node:path'

export default defineConfig({
  testDir: './e2e',
  testMatch: '**/research.spec.ts',
  timeout: 30000,
  retries: 0,
  workers: 1,
  reporter: [['list'], ['json', { outputFile: '../artifacts/browser_e2e_results.json' }]],
  outputDir: '../.local/e2e-results',
  use: {
    baseURL: 'http://127.0.0.1:8011',
    viewport: { width: 1440, height: 1000 },
    screenshot: 'only-on-failure',
    trace: 'on',
  },
  webServer: {
    // Regression cannot inherit billable provider configuration.
    env: {
      OPENAI_API_KEY: '',
      OXYPROOF_LLM_MODEL: '',
      OXYPROOF_LLM_PROVIDER: 'openai',
      OXYPROOF_OLLAMA_BASE_URL: '',
    },
    command:
      'uv run --offline --no-sync python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8011',
    cwd: path.resolve(import.meta.dirname, '..'),
    url: 'http://127.0.0.1:8011/api/health',
    reuseExistingServer: false,
    timeout: 30000,
  },
})
