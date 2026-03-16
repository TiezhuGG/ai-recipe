const rawApiBaseUrl = (import.meta.env.VITE_API_BASE_URL || '').trim().replace(/\/+$/, '')

export const API_BASE_URL = rawApiBaseUrl
export const API_ROOT = rawApiBaseUrl ? `${rawApiBaseUrl}/api` : '/api'

export function buildApiUrl(path: string): string {
  const normalizedPath = path.startsWith('/') ? path : `/${path}`
  return `${API_ROOT}${normalizedPath}`
}

export function resolveAssetUrl(assetUrl?: string | null): string | undefined {
  if (!assetUrl) {
    return undefined
  }

  if (/^https?:\/\//i.test(assetUrl) || assetUrl.startsWith('data:')) {
    return assetUrl
  }

  if (assetUrl.startsWith('/')) {
    return API_BASE_URL ? `${API_BASE_URL}${assetUrl}` : assetUrl
  }

  const normalizedAssetUrl = assetUrl.replace(/^\/+/, '')
  return API_BASE_URL ? `${API_BASE_URL}/${normalizedAssetUrl}` : `/${normalizedAssetUrl}`
}
