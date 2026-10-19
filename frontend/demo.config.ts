import { defineConfig } from '@playwright/test'
import base from './playwright.config'

export default defineConfig({
  ...base,
  testMatch: '**/demo.capture.ts',
  timeout: 260000,
  reporter: [['list']],
  outputDir: '../.local/demo-capture',
  use: {
    ...base.use,
    viewport: { width: 1440, height: 1000 },
    video: { mode: 'on', size: { width: 1440, height: 1000 } },
  },
})
