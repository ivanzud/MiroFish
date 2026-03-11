export const API_BASE_OVERRIDE_KEY = 'mirofish-api-base-url'

export const normalizeBaseURL = (value) => {
  const trimmedValue = value?.trim()
  if (!trimmedValue) {
    return ''
  }

  return trimmedValue.replace(/\/+$/, '')
}

export const getStoredBaseURL = (storage = globalThis?.localStorage) => {
  if (!storage) {
    return ''
  }

  try {
    return normalizeBaseURL(storage.getItem(API_BASE_OVERRIDE_KEY))
  } catch {
    return ''
  }
}

export const setStoredBaseURL = (value, storage = globalThis?.localStorage) => {
  if (!storage) {
    return ''
  }

  const normalizedValue = normalizeBaseURL(value)
  try {
    if (normalizedValue) {
      storage.setItem(API_BASE_OVERRIDE_KEY, normalizedValue)
    } else {
      storage.removeItem(API_BASE_OVERRIDE_KEY)
    }
  } catch {
    return ''
  }

  return normalizedValue
}

export const clearStoredBaseURL = (storage = globalThis?.localStorage) => {
  if (!storage) {
    return
  }

  try {
    storage.removeItem(API_BASE_OVERRIDE_KEY)
  } catch {
    // Ignore storage failures and fall back to auto-detection.
  }
}

export const resolveBaseURL = ({ runtimeBaseURL, envBaseURL, location } = {}) => {
  const trimmedRuntimeBaseURL = normalizeBaseURL(runtimeBaseURL)
  if (trimmedRuntimeBaseURL) {
    return trimmedRuntimeBaseURL
  }

  const trimmedEnvBaseURL = normalizeBaseURL(envBaseURL)
  if (trimmedEnvBaseURL) {
    return trimmedEnvBaseURL
  }

  if (!location) {
    return ''
  }

  const origin = location.origin || `${location.protocol}//${location.host}`
  if (!origin) {
    return ''
  }

  if (location.port === '3000') {
    const backendOrigin = new URL(origin)
    backendOrigin.port = '5001'
    return backendOrigin.origin
  }

  return origin
}
