export type ApiErrorKind = 'network' | 'timeout' | 'session' | 'http' | 'protocol'

export class ApiError extends Error {
  kind: ApiErrorKind
  status: number
  constructor(message: string, kind: ApiErrorKind, status = 0) {
    super(message)
    this.name = 'ApiError'
    this.kind = kind
    this.status = status
  }
}

// A lost POST response does not establish whether the server committed it.
// Keep retries explicit so a reconnect cannot create duplicate runs or reviews.
export async function requestJson<T>(path: string, init: RequestInit = {}, timeoutMs = 20_000): Promise<T> {
  const controller = new AbortController()
  const timer = setTimeout(() => controller.abort(), timeoutMs)
  const mutation = !!init.method && !['GET', 'HEAD'].includes(init.method.toUpperCase())
  const uncertainty = mutation ? ' The action was not confirmed; check saved results before submitting again.' : ''
  try {
    const response = await fetch(path, { ...init, signal: controller.signal, credentials: 'same-origin' })
    if (response.status === 204) return undefined as T
    const raw = await response.text()
    let payload: any = null
    try { payload = JSON.parse(raw) } catch { /* Handle non-JSON gateway and SPA responses below. */ }
    if (!response.ok) {
      const message = typeof payload?.error?.message === 'string' ? payload.error.message : undefined
      if (response.status === 401) throw new ApiError(message || 'Sign in to continue.', 'session', 401)
      if ([502, 503, 504].includes(response.status)) {
        throw new ApiError(`The local API is unavailable. Start BoundaryLab and reconnect.${uncertainty}`, 'network', response.status)
      }
      throw new ApiError(message || (response.status === 422 ? 'Some input values are invalid. Review the source and try again.' : `Request failed (${response.status}).`), 'http', response.status)
    }
    if (!response.headers.get('content-type')?.includes('application/json') || payload === null) {
      throw new ApiError('The API returned an unexpected response. Check that the BoundaryLab service and /api proxy are running.', 'protocol', response.status)
    }
    return payload as T
  } catch (error) {
    if (error instanceof ApiError) throw error
    if (controller.signal.aborted) {
      throw new ApiError(`The API took too long to respond. Reconnect and check the result.${uncertainty}`, 'timeout')
    }
    throw new ApiError(`Cannot reach the local BoundaryLab server. Start it and reconnect.${uncertainty}`, 'network')
  } finally {
    clearTimeout(timer)
  }
}
