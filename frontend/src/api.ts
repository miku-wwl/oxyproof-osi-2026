export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, { ...init, signal: AbortSignal.timeout(35000) })
  const body = await response.json()
  if (!response.ok) {
    const detail = body.detail ?? body
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail))
  }
  return body as T
}

export function scientific(value: number): string {
  return value.toExponential(3)
}

export function downloadReport(report: unknown) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }),
  )
  const link = document.createElement('a')
  link.href = url
  link.download = 'oxyproof-audit.json'
  link.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}
