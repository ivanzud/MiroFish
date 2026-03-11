export const resolveBaseURL = ({ envBaseURL, location } = {}) => {
  const trimmedEnvBaseURL = envBaseURL?.trim()
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
